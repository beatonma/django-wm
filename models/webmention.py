import json
import logging

from django.db import models

import mf2py

from main.util import safe_read


log = logging.getLogger(__name__)


class Webmention(models.Model):
    source = models.CharField(
        max_length=100, help_text='Where this webmention came from')
    target = models.CharField(
        max_length=100, help_text='The page this webmention is about')

    sent_by = models.URLField(
        blank=True, max_length=100,
        help_text='Source address of the HTTP request that sent this '
                  'webmention')

    target_slug = models.CharField(
        max_length=255,
        help_text='The slug that corresponds with the given url', blank=True)

    approved = models.BooleanField(
        default=False,
        help_text='Allow this webmention to appear publicly')
    validated = models.BooleanField(
        default=False,
        help_text='True if both source and target have been validated, '
                  'confirmed to exist, and source really does link to target')

    notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    # Data from h-card of the source, if it exists
    hcard_homepage = models.URLField(
        blank=True,
        help_text='Homepage url parsed from source h-card. '
                  'Used as a key to retrieve full HCard')

    source_target_concat = models.CharField(
        max_length=200, null=True, unique=True, editable=False,
        help_text='Source and target concatenated together to '
                  'form a crude key')

    @classmethod
    def create(cls, src, trgt):
        wm = cls(source=src, target=trgt)
        return wm

    def approve(self):
        self.approved = True

    def save(self, *args, **kwargs):
        self.source_target_concat = '{}_{}'.format(self.source, self.target)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created']

    def __unicode__(self):
        return '{} -> {} [validated={}, approved={}]'.format(
            self.source, self.target, self.validated, self.approved)

    def __str__(self):
        return '{} -> {} [validated={}, approved={}]'.format(
            self.source, self.target, self.validated, self.approved)


class HCard(models.Model):
    name = models.CharField(
        blank=True, max_length=50, help_text='Name of the person/organisation')
    avatar = models.URLField(
        blank=True, help_text='Link to their profile image')
    homepage = models.URLField(
        blank=True, null=True, unique=True, help_text='Link to their homepage')
    json = models.TextField(
        blank=True, help_text='Raw json representation of this hcard')

    @classmethod
    def from_soup(cls, soup):
        card = None

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
