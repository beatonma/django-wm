"""
Mentions for sources that do not support webmentions.
Needs to be input manually.
"""

import logging

from mentions.models import MentionsBaseModel
from mentions.models.mixins.quotable import QuotableMixin

log = logging.getLogger(__name__)


class SimpleMention(QuotableMixin, MentionsBaseModel):
    """A 'fake' webmention, created manually by you.

    If you find your content mentioned somewhere that did not submit a Webmention
    you may manually create a SimpleMention to represent it instead.

    SimpleMentions are returned alongside actual Webmentions by the `/get` endpoint
    so you can display them as you would any other Webmention."""

    pass
