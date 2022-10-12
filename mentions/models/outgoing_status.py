from django.db import models

from mentions.models.base import MentionsBaseModel
from mentions.models.mixins import RetryableMixin

__all__ = [
    "OutgoingWebmentionStatus",
    "get_or_create_outgoing_webmention",
]


class OutgoingWebmentionStatus(RetryableMixin, MentionsBaseModel):
    """Status tracker for webmentions that you (attempt to) send from your server.

    Used primarily for logging of outgoing mentions.
    """

    source_url = models.URLField(
        help_text="The URL on your server where this mention originates",
    )
    target_url = models.URLField(
        help_text="The URL that you mentioned.",
    )
    target_webmention_endpoint = models.URLField(
        null=True,
        blank=True,
        help_text="The endpoint URL to which we sent the webmention",
    )
    status_message = models.CharField(
        max_length=1024,
        help_text="Success, or an explanation of what went wrong.",
    )
    response_code = models.PositiveIntegerField(default=0)

    successful = models.BooleanField(default=False)

    def __str__(self):
        return (
            f"[{'OK' if self.successful else 'Failed'}:{self.response_code}] "
            f"{self.source_url} -> {self.target_url}"
        )

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Outgoing Webmentions"


def get_or_create_outgoing_webmention(
    source_urlpath: str,
    target_url: str,
    reset_retries: bool = False,
) -> OutgoingWebmentionStatus:
    """Safely get or create a OutgoingWebmentionStatus instance for given URLs.

    Since version 3.0.0 the URLs are effectively treated as 'unique together',
    but there may exist 'duplicate' instances from a previous installation."""

    kwargs = {
        "source_url": source_urlpath,
        "target_url": target_url,
    }
    try:
        status = OutgoingWebmentionStatus.objects.get_or_create(**kwargs)[0]
    except OutgoingWebmentionStatus.MultipleObjectsReturned:
        status = OutgoingWebmentionStatus.objects.filter(**kwargs).first()

    if reset_retries:
        status.reset_retries()

    return status
