"""
Mentions for sources that do not support webmentions.
Needs to be input manually.
"""

import logging

from mentions.models import MentionsBaseModel
from mentions.models.mixins.quotable import QuotableMixin

log = logging.getLogger(__name__)


class SimpleMention(QuotableMixin, MentionsBaseModel):
    pass
