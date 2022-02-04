from typing import Dict, Iterable, List, Optional

from mentions.models import HCard, QuotableMixin, SimpleMention, Webmention


def serialize_mentions(mentions: Iterable[QuotableMixin]) -> List[Dict]:
    def _typeof(mention) -> str:
        if isinstance(mention, Webmention):
            return "webmention"
        elif isinstance(mention, SimpleMention):
            return "simple"
        else:
            raise ValueError(f"Unhandled mention type: {mention}")

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
