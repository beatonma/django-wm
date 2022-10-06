import logging
from typing import Optional

from django.db import models
from django.urls import reverse
from sample_app.compat import MentionableMixin

log = logging.getLogger(__name__)


class Article(MentionableMixin, models.Model):
    author = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    content = models.TextField()

    slug = None

    def all_text(self) -> str:
        return self.content

    def get_absolute_url(self) -> str:
        return reverse("article", args=[self.pk])

    @classmethod
    def resolve_from_url_kwargs(cls, article_id: int, **url_kwargs) -> "Article":
        return Article.objects.get(pk=article_id)

    def __str__(self):
        return f"{self.author}: {self.title}"


def create_article(
    author: str,
    target_url: str,
    mention_type: str,
    content: Optional[str] = None,
) -> Article:
    try:
        from mentions.models.mixins import IncomingMentionType

        _type = IncomingMentionType[mention_type].value if mention_type else ""
    except ImportError:
        _type = ""

    content = (
        content
        or f"""<p>This text mentions <a href="{target_url}" class="{_type}">this page</a></p>"""
    )

    article = Article.objects.create(
        author=author,
        title=f"About {target_url}",
        content=content,
        allow_outgoing_webmentions=True,
    )

    log.info(f"Create article {article} ({mention_type})")

    return article
