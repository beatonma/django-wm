from django.db import models

from mentions.models import MentionsBaseModel


class PendingIncomingWebmention(MentionsBaseModel):
    """Temporary store of data about an incoming webmention.

    Only used if settings.WEBMENTIONS_USE_CELERY is False.
    Use `manage.py pending_mentions` to process."""

    source_url = models.URLField(
        help_text="The URL of the content that mentions your content."
    )
    target_url = models.URLField(
        help_text="The URL of the page on your server that is being mentioned."
    )
    sent_by = models.URLField(help_text="The origin of the webmention request.")

    def __str__(self):
        return f"PendingIncomingWebmention: {self.source_url} -> {self.target_url}"

    class Meta:
        ordering = ["-created_at"]


class PendingOutgoingContent(MentionsBaseModel):
    """Temporary store of data about content that may contain outgoing webmentions.

    Use `manage.py pending_mentions` to process."""

    absolute_url = models.URLField(
        help_text="URL on our server where the content can be found."
    )
    text = models.TextField(
        help_text="Text that may contain mentionable links. (retrieved via MentionableMixin.all_text())"
    )

    def __str__(self):
        return f"PendingOutgoingContent: {self.absolute_url}"

    class Meta:
        ordering = ["-created_at"]
