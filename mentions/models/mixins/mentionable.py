import logging

from django.contrib.contenttypes.models import ContentType
from django.db import models

from mentions.models.webmention import Webmention
from mentions.tasks import process_outgoing_webmentions
from mentions.util import serialize_mentions

log = logging.getLogger(__name__)


class MentionableMixin(models.Model):
    class Meta:
        abstract = True

    allow_incoming_webmentions = models.BooleanField(default=True)
    allow_outgoing_webmentions = models.BooleanField(default=False)

    @property
    def mentions(self):
        ctype = ContentType.objects.get_for_model(self.__class__)
        webmentions = Webmention.objects.filter(
            content_type=ctype,
            object_id=self.id,
            approved=True,
            validated=True)
        # manual_mentions = TODO
        return webmentions

    def mentions_json(self):
        return serialize_mentions(self.mentions)

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
        log.warning(
            'This model extends WebMentionableMixin but has not '
            'implemented all_text() so outgoing webmentions will '
            'not work!')
        return ''

    def save(self, *args, **kwargs):
        if self.allow_outgoing_webmentions:
            log.info('Outgoing webmention processing task added to queue...')
            process_outgoing_webmentions.delay(self.get_absolute_url(), self.all_text())

        super().save(*args, **kwargs)
