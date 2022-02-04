import logging
from typing import List

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

        Typically this will just be the main text of your model but
        you may also want to include content from any other text fields
        such as a summary or abstract.

        Example:
            def all_text(self) -> str:
                return f'{self.introduction} {self.main_content}'
        """
        raise ImplementationRequired(
            f"{self.__class__.__name__} does not implement all_text()"
        )

    def save(self, *args, **kwargs):
        if self.allow_outgoing_webmentions:
            handle_outgoing_webmentions(self.get_absolute_url(), self.all_text())

        super().save(*args, **kwargs)
