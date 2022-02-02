import json
import logging
from functools import reduce
from typing import Optional

import mf2py
from bs4 import BeautifulSoup
from django.db import models

from mentions.exceptions import NotEnoughData
from mentions.models import MentionsBaseModel

log = logging.getLogger(__name__)


class HCard(MentionsBaseModel):
    """An h-card represents information about a person or organisation.

    Spec: https://microformats.org/wiki/h-card
    """

    name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Name of the person/organisation",
    )
    avatar = models.URLField(blank=True, help_text="Link to their profile image")
    homepage = models.URLField(
        blank=True, null=True, help_text="Link to their homepage"
    )
    json = models.TextField(
        blank=True, help_text="Raw json representation of this hcard"
    )

    @classmethod
    def from_soup(cls, soup: BeautifulSoup, save=False):
        """Create or update HCard(s) using data from a BeautifulSoup document.

        See https://github.com/microformats/mf2py"""
        parser = mf2py.Parser(doc=soup)
        parsed_data = parser.to_dict()
        for item in parsed_data.get("items", []):
            try:
                return _parse_hcard(item, save)
            except NotEnoughData as e:
                log.debug(e)
                continue

    def save(self, *args, **kwargs):
        """Workaround so that empty homepages can be accepted without violating
        'unique' requirement. This allows admin to check missing content manually."""
        if not self.homepage:
            self.homepage = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f'name="{self.name}", avatar="{self.avatar}", homepage="{self.homepage}"'


def _parse_hcard(item: dict, save: bool) -> Optional[HCard]:
    """Spec: https://github.com/microformats/mf2py"""
    if "h-card" in item.get("type"):
        log.debug("Reading h-card...")
        attrs = item.get("properties")
        if attrs:
            _name = attrs.get("name", [""])[0]
            _avatar = attrs.get("photo", [""])[0]
            _homepage = attrs.get("url", [None])[0]
            _json = json.dumps(item, sort_keys=True)

            require_one_of = [_name, _avatar, _homepage]
            has_required_fields = (
                reduce(lambda acc, value: acc + 1 if value else acc, require_one_of, 0)
                >= 1
            )

            if not has_required_fields:
                raise NotEnoughData(
                    "An HCard requires a value for at least one of 'name', 'avatar', 'homepage'"
                )

            card, _ = HCard.objects.get_or_create(homepage=_homepage)

            card.name = _name
            card.avatar = _avatar
            card.json = _json

            if save:
                card.save()

            return card
        else:
            log.debug('_parse_hcard could not read "properties"')
