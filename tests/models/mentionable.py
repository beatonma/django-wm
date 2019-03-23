import logging

from django.db import models

from mentions.models.mixins.mentionable import MentionableMixin

log = logging.getLogger(__name__)


class MentionableTestStub(MentionableMixin, models.Model):
    """Stub model for testing."""

    stub_id = models.CharField(max_length=10)
    slug = models.SlugField(unique=True, max_length=10)
