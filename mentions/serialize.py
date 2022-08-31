from typing import Dict, Iterable, List, Optional

from mentions.models import HCard, SimpleMention, Webmention
from mentions.models.mixins import QuotableMixin

__all__ = [
    "serialize_hcard",
    "serialize_mentions",
]


def serialize_mentions(mentions: Iterable[QuotableMixin]) -> List[Dict]:
    return [
        {
            "hcard": serialize_hcard(mention.hcard),
            "quote": mention.quote,
            "source_url": mention.source_url,
            "published": mention.published,
            "type": _typeof(mention),
        }
        for mention in mentions
    ]


def serialize_hcard(hcard: Optional[HCard]) -> Optional[Dict]:
    if hcard is None:
        return None

    return {
        "name": hcard.name,
        "avatar": hcard.avatar,
        "homepage": hcard.homepage,
    }


def _typeof(mention) -> str:
    if isinstance(mention, Webmention):
        return mention.post_type or "webmention"

    if isinstance(mention, SimpleMention):
        return "simple"

    raise ValueError(f"Unhandled mention type: {mention}")
