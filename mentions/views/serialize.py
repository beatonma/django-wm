"""JSON serialization for web endpoints."""

from typing import Dict, Iterable, List, Optional

from mentions.models import HCard, SimpleMention, Webmention
from mentions.models.mixins import IncomingMentionType, QuotableMixin

__all__ = [
    "serialize_hcard",
    "serialize_mention",
    "serialize_mentions",
    "serialize_mentions_by_type",
]

from mentions.views import contract


def serialize_mention(mention: QuotableMixin) -> Dict:
    return {
        contract.HCARD: serialize_hcard(mention.hcard),
        contract.MENTION_QUOTE: mention.quote,
        contract.SOURCE_URL: mention.source_url,
        contract.MENTION_PUBLISHED: mention.published,
        contract.MENTION_TYPE: _typeof(mention),
    }


def serialize_mentions(mentions: Iterable[QuotableMixin]) -> List[Dict]:
    return [serialize_mention(mention) for mention in mentions]


def serialize_mentions_by_type(
    mentions: Iterable[QuotableMixin],
) -> Dict[str, List[Dict]]:
    type_names = IncomingMentionType.serialized_names() + [
        contract.MENTION_TYPE_DEFAULT,
        contract.MENTION_TYPE_SIMPLE,
    ]
    types = {name: [] for name in type_names}

    for mention in mentions:
        types[_typeof(mention)].append(serialize_mention(mention))

    return types


def serialize_hcard(hcard: Optional[HCard]) -> Optional[Dict]:
    if hcard is None:
        return None

    return {
        contract.HCARD_NAME: hcard.name,
        contract.HCARD_AVATAR: hcard.avatar,
        contract.HCARD_HOMEPAGE: hcard.homepage,
    }


def _typeof(mention) -> str:
    if isinstance(mention, Webmention):
        return mention.post_type or contract.MENTION_TYPE_DEFAULT

    if isinstance(mention, SimpleMention):
        return contract.MENTION_TYPE_SIMPLE

    raise ValueError(f"Unhandled mention type: {mention}")
