from django.db import models

from mentions.models.base import MentionsBaseModel
from mentions.models.mixins import RetryableMixin

__all__ = [
    "OutgoingWebmentionStatus",
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
