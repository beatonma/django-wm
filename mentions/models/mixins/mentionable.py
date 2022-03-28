import logging
from typing import List, Type

from django.contrib.contenttypes.models import ContentType
from django.db import models

from mentions.exceptions import ImplementationRequired
from mentions.models import QuotableMixin, SimpleMention
from mentions.models.webmention import Webmention
from mentions.serialize import serialize_mentions
from mentions.tasks.scheduling import handle_outgoing_webmentions

log = logging.getLogger(__name__)


class MentionableMixin(models.Model):
    class Meta:
        abstract = True

    allow_incoming_webmentions = models.BooleanField(default=True)
    allow_outgoing_webmentions = models.BooleanField(default=False)

    # `slug` field is no longer required as of version 2.3.0.
    # It may be removed in a future update, but for now we use it to provide
    # a default implementation of :func:`resolve_from_url_kwargs`
    slug = models.SlugField(unique=True)

    @property
    def mentions(self) -> List[QuotableMixin]:
        ctype = ContentType.objects.get_for_model(self.__class__)
        webmentions = Webmention.objects.filter(
            content_type=ctype,
            object_id=self.id,
            approved=True,
            validated=True,
        )
        simple_mentions = SimpleMention.objects.filter(
            content_type=ctype,
            object_id=self.id,
        )
        return list(webmentions) + list(simple_mentions)

    def mentions_json(self):
        return serialize_mentions(self.mentions)

    def get_absolute_url(self):
        raise ImplementationRequired(
            f"{self.__class__.__name__} does not implement get_absolute_url()"
        )

    def all_text(self) -> str:
        """
        Return all the text that should be searched when looking for
        outgoing Webmentions. Any URLs found in this text will be
        checked for webmention support.

        Typically this will just be the main text of your model, but
        you may also want to include content from any other text fields
        such as a summary or abstract.

        Example:
            def all_text(self) -> str:
                return f'{self.introduction} {self.main_content}'
        """
        raise ImplementationRequired(
            f"{self.__class__.__name__} does not implement all_text()"
        )

    @classmethod
    def resolve_from_url_kwargs(cls, **url_kwargs) -> Type["MentionableMixin"]:
        """Resolve a model instance from the given URL captured values.

        By default, an object is resolved via its unique slug.

        If your model does not have a unique slug, override this classmethod
        to retrieve an object using the URL parameters in url_kwargs.

        e.g.
        If your urlpatterns path looks like
            "<int:year>/<slug:slug>/",

        then you might override this method as:
            @classmethod
            def resolve_from_url_kwargs(cls, year: int, slug: str, **url_kwargs):
                return cls.objects.get(date__year=year, slug=slug)
        """
        return cls.objects.get(slug=url_kwargs.get("slug"))

    def save(self, *args, **kwargs):
        if self.allow_outgoing_webmentions:
            handle_outgoing_webmentions(self.get_absolute_url(), self.all_text())

        super().save(*args, **kwargs)
