import json
import logging

from django.db import models

import mf2py

from main.util import safe_read


log = logging.getLogger(__name__)


class HCard(models.Model):
    name = models.CharField(
        blank=True, max_length=50, help_text='Name of the person/organisation')
    avatar = models.URLField(
        blank=True, help_text='Link to their profile image')
    homepage = models.URLField(
        blank=True, null=True, help_text='Link to their homepage')
    json = models.TextField(
        blank=True, help_text='Raw json representation of this hcard')

    @classmethod
    def from_soup(cls, soup):
        card = None

        # TODO clean this up
        # https://github.com/microformats/mf2py

        parser = mf2py.Parser(doc=soup)
        j = json.loads(parser.to_json())
        for item in j['items']:
            if 'h-card' in safe_read(item, 'type', []):
                log.debug('Reading h-card...')
                attrs = safe_read(item, 'properties', None)
                if attrs:
                    _name = safe_read(attrs, 'name', [''])[0]
                    _avatar = safe_read(attrs, 'photo', [''])[0]
                    _homepage = safe_read(attrs, 'url', [''])[0]
                    _json = json.dumps(item, sort_keys=True)

                    if not _name and not _homepage:
                        log.info(
                            'h-card has neither a name nor a link: {}'.format(
                                attrs))
                        continue

                    card, _ = HCard.objects.get_or_create(homepage=_homepage)

                    card.name = _name
                    card.avatar = _avatar
                    card.json = _json
                    break
                else:
                    log.info('Could not read "properties"')
        return card

    def save(self, *args, **kwargs):
        # Workaround so that empty homepages can be accepted without
        # violating 'unique' requirement
        if not self.homepage:
            self.homepage = None

        super().save(*args, **kwargs)

    def __str__(self):
        return 'name="{}", avatar="{}", homepage="{}"'.format(
            self.name, self.avatar, self.homepage)
