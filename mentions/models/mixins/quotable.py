from enum import Enum
from typing import List, Tuple

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

__all__ = [
    "IncomingMentionType",
    "QuotableMixin",
]


class IncomingMentionType(Enum):
    """Properties that describe the context of the incoming webmention.

    See: https://microformats.org/wiki/h-entry"""

    Bookmark = "u-bookmark-of"
    Like = "u-like-of"
    Listen = "u-listen-of"
    Reply = "u-in-reply-to"
    Repost = "u-repost-of"
    Translation = "u-translation-of"
    Watch = "u-watch-of"

    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        return [(x.lower(), x) for x in cls.__members__.keys()]


class QuotableMixin(models.Model):
    """A third-party thing that talks about a first-party thing."""

    class Meta:
        abstract = True

    target_url = models.URLField(help_text="Our URL that is mentioned")
    source_url = models.URLField(help_text="The URL that mentions our content")

    quote = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text="A short excerpt from the quoted piece",
    )

    post_type = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="Type (e.g. like, reply, etc.) of mention, if specified",
        choices=IncomingMentionType.choices(),
    )

    published = models.DateTimeField(default=timezone.now)

    hcard = models.ForeignKey(
        "HCard",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    # The mention target may be an instance of any class that
    # uses the MentionableMixin so we need to use a GenericForeignKey
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    target_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return (
            f"{_trim_to_length(self.source_url)} -> {_trim_to_length(self.target_url)}"
        )


def _trim_to_length(text: str, max_length=32) -> str:
    if len(text) >= max_length:
        return f"{text[:max_length - 1]}…"
    else:
        return text
