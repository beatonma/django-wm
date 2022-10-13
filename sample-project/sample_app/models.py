import logging
import random
from typing import Optional

from django.db import models
from django.urls import reverse
from sample_app.compat import MentionableMixin

log = logging.getLogger(__name__)


class BasePost(models.Model):
    class Meta:
        abstract = True

    author = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    content = models.TextField()

    def all_text(self) -> str:
        return self.content

    def __str__(self):
        return f"{self.author}: {self.title}"


class Article(BasePost, MentionableMixin, models.Model):
    """Manual urlpatterns configuration, requires `resolve_from_url_kwargs`."""

    def get_absolute_url(self) -> str:
        return reverse("article", args=[self.pk])

    @classmethod
    def resolve_from_url_kwargs(cls, article_id: int, **url_kwargs) -> "Article":
        return Article.objects.get(pk=article_id)


class Blog(BasePost, MentionableMixin, models.Model):
    """Using `mentions_path` helper."""

    def get_absolute_url(self) -> str:
        return reverse("blog", args=[self.pk])


def create_article(
    author: str,
    target_url: str,
    mention_type: str,
    content: Optional[str] = None,
) -> BasePost:
    try:
        from mentions.models.mixins import IncomingMentionType

        _type = IncomingMentionType[mention_type].value if mention_type else ""
    except ImportError:
        _type = ""

    content = (
        content
        or f"""<p>This text mentions <a href="{target_url}" class="{_type}">this page</a></p>"""
    )

    model_class = Article if random.random() > 0.5 else Blog

    post = model_class.objects.create(
        author=author,
        title=f"About {target_url}",
        content=content,
        allow_outgoing_webmentions=True,
    )

    log.info(f"Create {model_class.__name__} {post} ({mention_type})")

    return post
