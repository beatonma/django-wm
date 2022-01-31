"""Models that are only used for testing."""

import logging

from django.db import models
from django.urls import reverse

from mentions.models.mixins.mentionable import MentionableMixin
from mentions.tests.util import viewname

log = logging.getLogger(__name__)


class MentionableTestModel(MentionableMixin, models.Model):
    """Stub model for testing."""

    content = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        abs_url = reverse(viewname.with_all_endpoints, args=[self.slug])
        return abs_url

    def all_text(self):
        return self.content
