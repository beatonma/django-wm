"""Models that are only used for testing."""

import logging

from django.db import models
from django.urls import reverse

from mentions.models.mixins.mentionable import MentionableMixin
from mentions.tests.util.constants import view_all_endpoints

log = logging.getLogger(__name__)


class MentionableTestModel(MentionableMixin, models.Model):
    """Stub model for testing."""

    stub_id = models.CharField(max_length=16)
    slug = models.SlugField(unique=True, max_length=20)

    content = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        abs_url = reverse(view_all_endpoints, args=[self.slug])
        log.info(abs_url)
        return abs_url

    def all_text(self):
        return self.content
