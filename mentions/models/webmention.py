import logging

from django.conf import settings
from django.db import models

from .base import MentionsBaseModel
from .mixins.quotable import QuotableMixin

log = logging.getLogger(__name__)


def _approve_default():
    if hasattr(settings, 'WEBMENTIONS_AUTO_APPROVE'):
        return settings.WEBMENTIONS_AUTO_APPROVE
    return False


class Webmention(QuotableMixin, MentionsBaseModel):
    """An incoming webmention that is received by your server."""
    sent_by = models.URLField(
        blank=True,
        help_text='Source address of the HTTP request that sent this '
                  'webmention')

    approved = models.BooleanField(
        default=_approve_default,
        help_text='Allow this webmention to appear publicly')
    validated = models.BooleanField(
        default=False,
        help_text='True if both source and target have been validated, '
                  'confirmed to exist, and source really does link to target')

    notes = models.CharField(max_length=1024, blank=True)

    @classmethod
    def create(cls, source_url, target_url, sent_by=None):
        return cls(source_url=source_url, target_url=target_url, sent_by=sent_by)

    def approve(self):
        self.approved = True

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ('approve_webmention', 'Can approve received Webmentions for publishing.')
        ]

    def __str__(self):
        return (f'{self.source_url} -> {self.target_url} '
                f'[validated={self.validated}, approved={self.approved},'
                f'content_type={self.content_type}, id={self.object_id}]')


class OutgoingWebmentionStatus(MentionsBaseModel):
    """Status tracker for webmentions that you (attempt to) send from your server.

    Currently used primarily for logging of outgoing mentions.
    """
    source_url = models.URLField(
        help_text='The URL on your server where this mention originates',
    )
    target_url = models.URLField(
        help_text='The URL that you mentioned.',
    )
    target_webmention_endpoint = models.URLField(
        null=True,
        blank=True,
        help_text='The endpoint URL to which we sent the webmention',
    )
    status_message = models.CharField(
        max_length=1024,
        help_text='Success, or an explanation of what went wrong.',
    )
    response_code = models.PositiveIntegerField(default=0)

    successful = models.BooleanField(default=False)

    def __str__(self):
        return (f'{self.source_url} -> {self.target_url} '
                f'(endpoint={self.target_webmention_endpoint}): '
                f'[{self.successful}] {self.status_message} '
                f'[{self.response_code}]')

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Outgoing Webmention Statuses'
