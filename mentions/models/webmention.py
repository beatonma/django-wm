import logging

from django.conf import settings
from django.db import models

from .mixins.quotable import QuotableMixin

log = logging.getLogger(__name__)


def _approve_default():
    if hasattr(settings, 'WEBMENTIONS_AUTO_APPROVE'):
        return settings.WEBMENTIONS_AUTO_APPROVE
    return False


class Webmention(QuotableMixin, models.Model):
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

    notes = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, source_url, target_url, sent_by=None):
        return cls(source_url=source_url, target_url=target_url, sent_by=sent_by)

    def approve(self):
        self.approved = True

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return (f'{self.source_url} -> {self.target_url} '
                f'[validated={self.validated}, approved={self.approved},'
                f'content_type={self.content_type}, id={self.object_id}]')
