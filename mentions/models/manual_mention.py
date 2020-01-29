"""
Mentions for sources that do not support webmentions.
Needs to be input manually.
"""

import logging

from . import MentionsBaseModel
from .mixins.quotable import QuotableMixin


log = logging.getLogger(__name__)


class SimpleMention(QuotableMixin, MentionsBaseModel):
    pass
