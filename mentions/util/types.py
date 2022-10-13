from typing import TypeVar

from mentions.models.mixins import MentionableMixin

MentionableImpl = TypeVar("MentionableImpl", bound=MentionableMixin)
