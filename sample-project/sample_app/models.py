import datetime
import logging

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from sample_app.compat import MentionableMixin

log = logging.getLogger(__name__)


class Article(MentionableMixin, models.Model):
    author = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    content = models.TextField()
    allow_incoming_webmentions = models.BooleanField(
        default=True,
        help_text="Just for testing upgrade from 2.3.0 -> 3.0.0",
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(
                datetime.datetime.now().strftime(
                    f"%y%m%d-%H%M%S-{self.author}-{self.title}"
                )
            )[:32]
        super().save(*args, **kwargs)

    def all_text(self) -> str:
        return self.content

    def get_absolute_url(self):
        return reverse("article", args=[self.pk])

    @classmethod
    def resolve_from_url_kwargs(cls, article_id: int, **url_kwargs) -> "Article":
        return Article.objects.get(pk=article_id)

    def __str__(self):
        return f"{self.author}: {self.title}"


def create_article(author: str, target_url: str, mention_type: str) -> Article:
    try:
        from mentions.models.mixins import IncomingMentionType

        _type = IncomingMentionType[mention_type].value if mention_type else ""
    except ImportError:
        _type = ""

    article = Article.objects.create(
        author=author,
        title=f"About {target_url}",
        content=f"""<p>This text mentions <a href="{target_url}" class="{_type}">this page</a></p>""",
        allow_outgoing_webmentions=True,
    )

    log.info(f"Create article {article} ({mention_type})")

    return article
