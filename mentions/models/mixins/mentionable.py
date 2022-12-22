import logging
from typing import List, Type

from django.db import models
from django.utils.translation import gettext_lazy as _

from mentions import options
from mentions.exceptions import ImplementationRequired
from mentions.models.mixins.quotable import QuotableMixin

__all__ = [
    "MentionableMixin",
]

log = logging.getLogger(__name__)


def _outgoing_default():
    return options.allow_outgoing_default()


class MentionableMixin(models.Model):
    class Meta:
        abstract = True

    allow_outgoing_webmentions = models.BooleanField(
        _("allow outgoing webmentions"),
        default=_outgoing_default,
    )

    def get_mentions(self) -> List[QuotableMixin]:
        from mentions.resolution import get_mentions_for_object

        return get_mentions_for_object(self)

    def get_mentions_json(self) -> List[dict]:
        from mentions.views.serialize import serialize_mentions

        return serialize_mentions(self.get_mentions())

    def get_absolute_url(self):
        raise ImplementationRequired(
            f"{self.__class__.__name__} does not implement get_absolute_url()"
        )

    def get_content_html(self) -> str:
        """
        Return all the HTML-formatted text that should be searched when looking
        for outgoing Webmentions. Any <a> tags found in this content will be
        checked for webmention support.

        Typically this will just be the main text of your model, but
        you may also want to include content from any other text fields
        such as a summary or abstract.

        Example:
            def get_content_html(self) -> str:
                return f'{self.introduction} {self.main_content}'
        """

        log.warning(
            "Method `MentionableMixin.all_text()` is deprecated, replaced by "
            "`MentionableMixin.get_content_html()`. Please rename the method "
            f"on your model `{self.__class__.__name__}`."
        )

        return self.all_text()

    @classmethod
    def resolve_from_url_kwargs(
        cls: Type["MentionableMixin"],
        **url_kwargs,
    ) -> "MentionableMixin":
        """Resolve a model instance from the given URL captured values.

        You can skip implementing this if you use one of the `urlpatterns`
        helpers: `mentions_path` or `mentions_re_path`.

        By default, an object is resolved via its id using the object_id kwarg.

        You may override this classmethod to retrieve an object using any
        URL parameters in url_kwargs.

        e.g.
        If your urlpatterns path looks like
            "<int:year>/<slug:slug>/",

        then you might override this method as:
            @classmethod
            def resolve_from_url_kwargs(cls, year: int, slug: str, **url_kwargs):
                return cls.objects.get(date__year=year, slug=slug)
        """
        param_mapping = options.default_url_parameter_mapping()
        query = {
            model_field: url_kwargs.get(url_param)
            for url_param, model_field in param_mapping.items()
        }

        return cls.objects.get(**query)

    def should_process_webmentions(self) -> bool:
        """Return True if this instance should process webmentions when saved."""
        return self.allow_outgoing_webmentions

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.should_process_webmentions():
            from mentions.tasks import handle_outgoing_webmentions

            handle_outgoing_webmentions(
                self.get_absolute_url(), self.get_content_html()
            )

    # Deprecated methods below this point
    def mentions(self) -> List[QuotableMixin]:
        """Deprecated in 4.0: Replaced by `get_mentions()`."""
        log.warning(
            "Method `MentionableMixin.mentions()` is deprecated, replaced by "
            "`MentionableMixin.get_mentions()`."
        )
        return self.get_mentions()

    def mentions_json(self):
        """Deprecated in 4.0: Replaced by `get_mentions_json()`."""
        log.warning(
            "Method `MentionableMixin.mentions_json()` is deprecated, replaced by "
            "`MentionableMixin.get_mentions_json()`."
        )
        return self.get_mentions_json()

    def all_text(self) -> str:
        """Deprecated in 4.0: Replaced by `get_content_html()`.

        Only the name has changed - purpose and signature are the same."""
        raise ImplementationRequired(
            f"{self.__class__.__name__} does not implement get_content_html()"
        )
