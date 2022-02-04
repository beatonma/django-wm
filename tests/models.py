"""Models that are only used for testing."""

import logging

from django.db import models
from django.urls import reverse

from mentions.models.mixins.mentionable import MentionableMixin
from tests.util import viewname

log = logging.getLogger(__name__)


class MentionableTestModel(MentionableMixin, models.Model):
    """Basic mentionable model with all required methods implemented."""

    content = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse(viewname.with_target_object_view, args=[self.slug])

    def all_text(self):
        return self.content

    class Meta:
        app_label = "tests"


class BadTestModelMissingGetAbsoluteUrl(MentionableMixin, models.Model):
    """A MentionableMixin model that forgot to implement get_absolute_url()"""

    content = models.TextField(blank=True, null=True)

    def all_text(self):
        return self.content

    class Meta:
        app_label = "tests"


class BadTestModelMissingAllText(MentionableMixin, models.Model):
    """A MentionableMixin model that forgot to implement all_text()"""

    content = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse(viewname.with_target_object_view, args=[self.slug])

    class Meta:
        app_label = "tests"
