from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _

from mentions.models.base import MentionsBaseModel
from mentions.models.mixins import RetryableMixin

__all__ = [
    "PendingIncomingWebmention",
    "PendingOutgoingContent",
]


class PendingIncomingWebmention(RetryableMixin, MentionsBaseModel):
    """Temporary store of data about an incoming webmention.

    Only used if settings.WEBMENTIONS_USE_CELERY is False.
    Use `manage.py pending_mentions` to process."""

    source_url = models.URLField(
        _("source URL"),
        help_text=_("The URL of the content that mentions your content."),
    )
    target_url = models.URLField(
        _("target URL"),
        help_text=_("The URL of the page on your server that is being mentioned."),
    )
    sent_by = models.URLField(
        _("sent by"),
        help_text=_("The origin of the webmention request."),
    )

    def __str__(self):
        return f"PendingIncomingWebmention: {self.source_url} -> {self.target_url}"

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=("source_url", "target_url"),
                name="unique_source_url_per_target_url",
            ),
        ]
        ordering = ["-created_at"]
        verbose_name = _("pending incoming webmention")
        verbose_name_plural = _("pending incoming webmentions")


class PendingOutgoingContent(MentionsBaseModel):
    """Temporary store of data about content that may contain outgoing webmentions.

    Use `manage.py pending_mentions` to process."""

    absolute_url = models.URLField(
        _("absolute URL"),
        help_text=_("URL on our server where the content can be found."),
        unique=True,
    )
    text = models.TextField(
        _("HTML content"),
        help_text=_("HTML text that may contain mentionable links."),
    )

    def __str__(self):
        return f"PendingOutgoingContent: {self.absolute_url}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("pending outgoing content")
        verbose_name_plural = _("pending outgoing content")
