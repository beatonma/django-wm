import json
from functools import reduce
from typing import List, Optional

import mf2py
from bs4 import BeautifulSoup

from mentions.exceptions import NotEnoughData
from mentions.models import HCard

CLASS_H_CARD = "h-card"
CLASS_H_ENTRY = "h-entry"
CLASS_H_FEED = "h-feed"


def parse_hcard(soup: BeautifulSoup) -> Optional[HCard]:
    """Create or update HCard(s) using data from a BeautifulSoup document.

    See https://github.com/microformats/mf2py"""

    parser = mf2py.Parser(doc=soup)
    parsed_data = parser.to_dict()
    items = parsed_data.get("items", [])
    return find_hcard(items)


def find_hcard(data: List[dict]) -> Optional[HCard]:
    """Try to find a representative `h-card` element.

    `h-card` may be a standalone (top-level) element, or it may be embedded in
    `h-entry` or `h-feed` containers.

    We look for it at the top level first before diving deeper.

    Args:
        data: Parsed microformat data
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

        elif CLASS_H_ENTRY in _type or CLASS_H_FEED in _type:
            fallback.append(item)

    return _find_embedded_hcard(fallback)


def _find_embedded_hcard(items: List[dict]) -> Optional[HCard]:
    """Traverse `h-entry` and `h-feed` containers to find an `h-card`"""

    for item in items:
        print(json.dumps(item, indent=2))
        _type = item.get("type")
        props = item.get("properties")

        if "author" in props:
            return find_hcard(props.get("author"))

        elif CLASS_H_FEED in _type:
            return find_hcard(item.get("children", []))

        else:
            print(f"Unhandled embedded content: {item}")


def _create_hcard(data: dict) -> HCard:
    props = data.get("properties")
    homepage = props.get("url", [None])[0]
    name = props.get("name", [""])[0]
    avatar = props.get("photo", [""])[0]
    _json = json.dumps(data, sort_keys=True)

    _require_any_of([name, homepage])

    if homepage:
        card, _ = HCard.objects.update_or_create(
            homepage=homepage,
            defaults=dict(
                name=name,
                avatar=avatar,
                json=_json,
            ),
        )

    else:
        card, _ = HCard.objects.update_or_create(
            name=name,
            defaults=dict(
                avatar=avatar,
                json=_json,
            ),
        )

    return card


def _require_any_of(fields: List[str]):
    has_required_fields = (
        reduce(lambda acc, value: acc + 1 if value else acc, fields, 0) >= 1
    )

    if not has_required_fields:
        raise NotEnoughData(
            "An HCard requires a value for at least one of 'name', 'homepage'"
        )
