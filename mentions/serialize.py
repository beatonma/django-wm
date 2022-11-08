from typing import Dict, Iterable, List, Optional

from mentions.models import HCard, SimpleMention, Webmention
from mentions.models.mixins import IncomingMentionType, QuotableMixin

__all__ = [
    "serialize_hcard",
    "serialize_mentions",
    "serialize_mentions_by_type",
]

TYPE_DEFAULT = "webmention"
TYPE_SIMPLE = "simple"


def serialize_mention(mention: QuotableMixin) -> Dict:
    return {
        "hcard": serialize_hcard(mention.hcard),
        "quote": mention.quote,
        "source_url": mention.source_url,
        "published": mention.published,
        "type": _typeof(mention),
    }


def serialize_mentions(mentions: Iterable[QuotableMixin]) -> List[Dict]:
    return [serialize_mention(mention) for mention in mentions]


def serialize_mentions_by_type(
    mentions: Iterable[QuotableMixin],
) -> Dict[str, List[Dict]]:
    type_names = IncomingMentionType.serialized_names() + [TYPE_DEFAULT, TYPE_SIMPLE]
    types = {name: [] for name in type_names}

    for mention in mentions:
        types[_typeof(mention)].append(serialize_mention(mention))

    return types


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
        return mention.post_type or TYPE_DEFAULT

    if isinstance(mention, SimpleMention):
        return TYPE_SIMPLE

    raise ValueError(f"Unhandled mention type: {mention}")
