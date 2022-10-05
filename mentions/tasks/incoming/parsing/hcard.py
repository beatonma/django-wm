import json
from functools import reduce
from typing import List, Optional

import mf2py
from bs4 import Tag

from mentions.exceptions import NotEnoughData
from mentions.models import HCard

__all__ = [
    "parse_hcard",
    "find_related_hcard",
]

from mentions.resolution import update_or_create_hcard

CLASS_H_CARD = "h-card"
CLASS_H_ENTRY = "h-entry"
CLASS_H_FEED = "h-feed"


def parse_hcard(
    soup: Tag,
    recursive: bool = False,
) -> Optional[HCard]:
    """Create or update HCard(s) using data from a BeautifulSoup document.

    See https://github.com/microformats/mf2py"""

    parser = mf2py.Parser(doc=soup)
    parsed_data = parser.to_dict()
    items = parsed_data.get("items", [])
    return _find_hcard(items, recursive=recursive)


def find_related_hcard(link: Tag) -> Optional[HCard]:
    """Try to find a post-specific h-card from a parent `h-entry` or `h-feed`."""
    hentry = link.find_parent(class_=CLASS_H_ENTRY)
    if hentry:
        hcard = parse_hcard(hentry, recursive=True)
        if hcard:
            return hcard

    hfeed = link.find_parent(class_=CLASS_H_FEED)
    if hfeed:
        hcard = parse_hcard(hfeed, recursive=True)
        if hcard:
            return hcard


def _find_hcard(data: List[dict], recursive: bool = False) -> Optional[HCard]:
    """Find a useful `h-card` in parsed microformats data.

    Args:
        data: Parsed microformat data
        recursive: If True, traverse h-feed and h-entry containers to try
                   find embedded h-card.
                   If False, h-card will only be found at the top level.
    """

    fallback = []  # List of items that may contain an embedded h-card

    for item in data:
        _type = item.get("type", [])

        if CLASS_H_CARD in _type:
            try:
                hcard = _create_hcard(item)
                if hcard:
                    return hcard

            except NotEnoughData:
                # This h-card is missing required fields, keep looking for a better-formed one.
                pass

        elif recursive and (CLASS_H_ENTRY in _type or CLASS_H_FEED in _type):
            fallback.append(item)

    if not recursive:
        return None

    return _find_embedded_hcard(fallback)


def _find_embedded_hcard(items: List[dict]) -> Optional[HCard]:
    """Traverse `h-entry` and `h-feed` containers to find an `h-card`"""

    if not items:
        return None

    for item in items:
        _type = item.get("type")
        props = item.get("properties")

        if "author" in props:
            return _find_hcard(props.get("author"))

        elif "children" in item:
            return _find_hcard(item.get("children", []))


def _create_hcard(data: dict) -> HCard:
    props = data.get("properties")
    homepage = props.get("url", [None])[0]
    name = props.get("name", [""])[0]
    avatar = props.get("photo", [""])[0]
    _json = json.dumps(data, sort_keys=True)

    _require_any_of([name, homepage])

    return update_or_create_hcard(
        homepage=homepage,
        name=name,
        avatar=avatar,
        data=_json,
    )


def _require_any_of(fields: List[str]):
    has_required_fields = (
        reduce(lambda acc, value: acc + 1 if value else acc, fields, 0) >= 1
    )

    if not has_required_fields:
        raise NotEnoughData(
            "An HCard requires a value for at least one of 'name', 'homepage'"
        )
