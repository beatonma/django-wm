"""Models that are only used for testing."""

import logging

from django.db import models
from django.urls import reverse
from django.utils import timezone

from mentions.models.mixins import MentionableMixin
from tests.tests.util import viewname

log = logging.getLogger(__name__)


class BaseModel(MentionableMixin, models.Model):
    class Meta:
        abstract = True
        app_label = "test_app"

    name = models.CharField(max_length=32, null=True, unique=True)
    content = models.TextField(blank=True, null=True)
    viewname = models.CharField(
        max_length=100,
        default=viewname.with_target_object_view,
    )


class MentionableTestModel(BaseModel):
    """Basic mentionable model with all required methods implemented."""

    def get_absolute_url(self):
        return reverse(self.viewname, args=[self.id])

    def get_content_html(self):
        return self.content


class BadTestModelMissingGetAbsoluteUrl(BaseModel):
    """A MentionableMixin model that forgot to implement get_absolute_url()"""

    def get_content_html(self):
        return self.content


class BadTestModelMissingAllText(BaseModel):
    """A MentionableMixin model that forgot to implement get_content_html()"""

    def get_absolute_url(self):
        return reverse(self.viewname, args=[self.id])


class SampleBlog(models.Model):
    slug = models.SlugField()


class MentionableTestBlogPost(BaseModel):
    """A MentionableMixin model with custom resolve_from_url_kwargs implementation.

    Models are now resolved using arbitrary kwargs from the relevant urlpatterns
    path - not necessarily just '<int:object_id>'.

    This model uses multiple slugs and date fields in its urlpatterns path,
    and we should be able to resolve from that path back to an instance of this
    model.
    """

    timestamp = models.DateTimeField(default=timezone.now)

    slug = models.SlugField(
        unique_for_date="timestamp",
        unique=False,
    )

    blog = models.ForeignKey(
        "SampleBlog",
        on_delete=models.CASCADE,
    )

    def get_content_html(self):
        return self.content

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
