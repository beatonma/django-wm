import logging

from django.db import models

from mentions.models.mixins.mentionable import MentionableMixin

log = logging.getLogger(__name__)


class MentionableTestModel(MentionableMixin, models.Model):
    """Stub model for testing."""

    stub_id = models.CharField(max_length=16)
    slug = models.SlugField(unique=True, max_length=20)

    content = models.TextField(blank=True, null=True)
