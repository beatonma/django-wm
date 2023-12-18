import json
from functools import reduce
from typing import List, Optional

import mf2py
from bs4 import Tag

from mentions.exceptions import NotEnoughData
from mentions.microformats import H_CARD, H_ENTRY, H_FEED
from mentions.models import HCard
from mentions.models.hcard import update_or_create_hcard

__all__ = [
    "parse_hcard",
    "find_related_hcard",
]


# Key names for mf2py parsing output
AUTHOR = "author"
CHILDREN = "children"
TYPE = "type"
PROPERTIES = "properties"
NAME = "name"
URL = "url"
PHOTO = "photo"
LOGO = "logo"


def parse_hcard(
    soup: Tag,
    recursive: bool = False,
) -> Optional[HCard]:
    """Create or update HCard using data from a BeautifulSoup document.

    Top-down search to find an h-card on the document.

    See https://github.com/microformats/mf2py"""

    parser = mf2py.Parser(doc=soup)
    parsed_data = parser.to_dict()
    items = parsed_data.get("items", [])
    return _find_hcard(items, recursive=recursive)


def find_related_hcard(link: Tag) -> Optional[HCard]:
    """Try to find a post-specific h-card from a parent `h-entry` or `h-feed`.

    Bottom-up search for the nearest related h-card."""
    hentry = link.find_parent(class_=H_ENTRY)
    if hentry:
        hcard = parse_hcard(hentry, recursive=True)
        if hcard:
            return hcard

    hfeed = link.find_parent(class_=H_FEED)
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
        _type = item.get(TYPE, [])

        if H_CARD in _type:
            try:
                hcard = _create_hcard(item)
                if hcard:
                    return hcard

            except NotEnoughData:
                # This h-card is missing required fields, keep looking for a better-formed one.
                pass

        elif recursive and (H_ENTRY in _type or H_FEED in _type):
            fallback.append(item)

    if not recursive:
        return None

    return _find_embedded_hcard(fallback)


def _find_embedded_hcard(items: List[dict]) -> Optional[HCard]:
    """Traverse `h-entry` and `h-feed` containers to find an `h-card`"""

    if not items:
        return None

    for item in items:
        _type = item.get(TYPE)
        props = item.get(PROPERTIES)

        if AUTHOR in props:
            return _find_hcard(props.get(AUTHOR))

        elif CHILDREN in item:
            return _find_hcard(item.get(CHILDREN, []))


def _create_hcard(data: dict) -> HCard:
    props = data.get(PROPERTIES)
    homepage = props.get(URL, [None])[0]
    name = props.get(NAME, [""])[0]
    avatar = props.get(PHOTO, [""])[0] or props.get(LOGO, [""])[0]

    if isinstance(avatar, dict):
        avatar = avatar.get("value", "")

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
