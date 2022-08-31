from django.db import models

from mentions import options
from mentions.models.base import MentionsBaseModel
from mentions.models.mixins import QuotableMixin

__all__ = [
    "Webmention",
]


def _approve_default():
    return options.auto_approve()


class Webmention(QuotableMixin, MentionsBaseModel):
    """An incoming webmention that is received by your server."""

    sent_by = models.URLField(
        blank=True,
        help_text="Source address of the HTTP request that sent this webmention",
    )

    approved = models.BooleanField(
        default=_approve_default, help_text="Allow this webmention to appear publicly"
    )
    validated = models.BooleanField(
        default=False,
        help_text="True if both source and target have been validated, "
        "confirmed to exist, and source really does link to target",
    )

    notes = models.CharField(
        max_length=1024,
        blank=True,
        help_text="A description of any errors encountered when building this Webmention.",
    )

    def approve(self):
        self.approved = True

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.source_url} -> {self.target_url} "
            f"[validated={self.validated}, approved={self.approved},"
            f"content_type={self.content_type}, id={self.object_id}]"
        )
