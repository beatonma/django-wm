import logging

from django.db import models
from django.urls import reverse

from mentions.models.mixins.mentionable import MentionableMixin

log = logging.getLogger(__name__)


class MentionableTestModel(MentionableMixin, models.Model):
    """Stub model for testing."""

    stub_id = models.CharField(max_length=16)
    slug = models.SlugField(unique=True, max_length=20)

    content = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        abs_url = reverse('all_endpoints_view', args=[self.slug])
        log.info(abs_url)
        return abs_url

    def all_text(self):
        return self.content
