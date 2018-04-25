import logging

from django.contrib.contenttypes.models import ContentType
from django.db import models

from mentions.models.webmention import Webmention
from mentions.tasks import process_outgoing_webmentions


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
            content_type__pk=ctype.id,
            object_id=self.id,
            approved=True,
            validated=True,)
        # manual_mentions = TODO
        return webmentions

    def mentions_json(self):
        mentions = self.mentions
        items = []
        for x in mentions:
            items.append({
                'hcard': x.hcard.as_json() if x.hcard else {},
                'quote': x.quote,
                'source_url': x.source_url,
                'published': x.published,
            })
        return items

    def all_text(self):
        log.warn(
            'This model extends WebMentionableMixin but has not '
            'implemented all_text() so outgoing webmentions will '
            'not work!')
        return ''

    def save(self, *args, **kwargs):
        if self.allow_outgoing_webmentions:
            process_outgoing_webmentions(
                self.get_absolute_url(), self.all_text())

        super().save(*args, **kwargs)
