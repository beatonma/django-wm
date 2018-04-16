import logging

from django.db import models

from .mixins.quotable import QuotableMixin


log = logging.getLogger(__name__)


class Webmention(QuotableMixin, models.Model):

    sent_by = models.URLField(
        blank=True,
        help_text='Source address of the HTTP request that sent this '
                  'webmention')

    approved = models.BooleanField(
        default=False,
        help_text='Allow this webmention to appear publicly')
    validated = models.BooleanField(
        default=False,
        help_text='True if both source and target have been validated, '
                  'confirmed to exist, and source really does link to target')

    notes = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, src, trgt):
        wm = cls(source_url=src, target_url=trgt)
        return wm

    def approve(self):
        self.approved = True

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return '{} -> {} [validated={}, approved={}]'.format(
            self.source, self.target, self.validated, self.approved)
