import json
import logging

from django.db import models

import mf2py

from main.models.mixins import ThemeableMixin


log = logging.getLogger(__name__)


class HCard(ThemeableMixin, models.Model):
    name = models.CharField(
        blank=True, max_length=50, help_text='Name of the person/organisation')
    avatar = models.URLField(
        blank=True, help_text='Link to their profile image')
    homepage = models.URLField(
        blank=True, null=True, help_text='Link to their homepage')
    json = models.TextField(
        blank=True, help_text='Raw json representation of this hcard')

    def as_json(self):
        return {
            'name': self.name,
            'avatar': self.avatar,
            'homepage': self.homepage,
            'primary_color': self.primary_color,
            'accent_color': self.accent_color,
            'foreground_color': ('var(--text-{}-primary)'
                                 .format(self.foreground_color))
        }

    @classmethod
    def from_soup(cls, soup):
        # https://github.com/microformats/mf2py
        parser = mf2py.Parser(doc=soup)
        j = parser.to_dict()
        for item in j['items']:
            if 'h-card' in item.get('type', []):
                log.debug('Reading h-card...')
                attrs = item.get('properties')
                if attrs:
                    _name = attrs.get('name', [''])[0]
                    _avatar = attrs.get('photo', [''])[0]
                    _homepage = attrs.get('url', [''])[0]
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
                    return card
                else:
                    log.info('Could not read "properties"')

    def save(self, *args, **kwargs):
        # Workaround so that empty homepages can be accepted without
        # violating 'unique' requirement
        if not self.homepage:
            self.homepage = None

        super().save(*args, **kwargs)

    def __str__(self):
        return 'name="{}", avatar="{}", homepage="{}"'.format(
            self.name, self.avatar, self.homepage)
