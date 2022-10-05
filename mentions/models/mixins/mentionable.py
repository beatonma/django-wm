from typing import List, Type

from django.db import models

from mentions.exceptions import ImplementationRequired
from mentions.models.mixins.quotable import QuotableMixin

__all__ = [
    "MentionableMixin",
]


class MentionableMixin(models.Model):
    class Meta:
        abstract = True

    allow_outgoing_webmentions = models.BooleanField(default=False)

    # `slug` field is no longer required as of version 2.3.0.
    # It may be removed in a future update, but for now we use it to provide
    # a default implementation of :func:`resolve_from_url_kwargs`
    slug = models.SlugField(unique=True)

    def mentions(self) -> List["QuotableMixin"]:
        from mentions.resolution import get_mentions_for_object

        return get_mentions_for_object(self)

    def mentions_json(self):
        from mentions.serialize import serialize_mentions

        return serialize_mentions(self.mentions())

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
    def resolve_from_url_kwargs(
        cls: Type["MentionableMixin"],
        **url_kwargs,
    ) -> "MentionableMixin":
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

    def should_process_webmentions(self) -> bool:
        """Return True if this instance should process webmentions when saved."""
        return self.allow_outgoing_webmentions

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.should_process_webmentions():
            from mentions.tasks import handle_outgoing_webmentions

            handle_outgoing_webmentions(self.get_absolute_url(), self.all_text())
