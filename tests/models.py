"""Models that are only used for testing."""

import logging

from django.db import models
from django.urls import reverse
from django.utils import timezone

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


class SampleBlog(models.Model):
    slug = models.SlugField()

    class Meta:
        app_label = "tests"


class MentionableTestBlogPost(MentionableMixin, models.Model):
    """A MentionableMixin model with custom resolve_from_url_kwargs implementation.

    Models are now resolved using arbitrary kwargs from the relevant urlpatterns
    path - not necessarily just '<slug:slug>'.

    This model uses multiple slugs and date fields in its urlpatterns path,
    and we should be able to resolve from that path back to an instance of this
    model.
    """

    content = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    slug = models.SlugField(
        unique_for_date="timestamp",
        unique=False,
    )

    blog = models.ForeignKey(
        "SampleBlog",
        on_delete=models.CASCADE,
    )

    def all_text(self):
        return self.content

    def get_absolute_url(self):
        return reverse(
            "weblogs:post_detail",
            kwargs={
                "blog_slug": self.blog.slug,
                "year": self.timestamp.strftime("%Y"),
                "month": self.timestamp.strftime("%m"),
                "day": self.timestamp.strftime("%d"),
                "post_slug": self.slug,
            },
        )

    @classmethod
    def resolve_from_url_kwargs(
        cls,
        blog_slug: str,
        year: int,
        month: int,
        day: int,
        post_slug: str,
        **url_kwargs: dict,
    ) -> "MentionableTestBlogPost":
        return cls.objects.get(
            blog__slug=blog_slug,
            timestamp__year=year,
            timestamp__month=month,
            timestamp__day=day,
            slug=post_slug,
        )

    class Meta:
        app_label = "tests"
