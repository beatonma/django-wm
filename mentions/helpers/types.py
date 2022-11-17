from typing import Dict, Sequence, Set, Tuple, TypeVar, Union

from mentions.models.mixins import MentionableMixin

"""
First item corresponds to captured kwarg from urlpatterns.
Second item defines the lookup on the model in the standard querying format:
  https://docs.djangoproject.com/en/stable/ref/models/querysets/#field-lookups
"""
ModelFieldMappingItem = Tuple[str, str]

ModelFieldMapping = Union[
    Dict[str, str],
    Sequence[str],
    Set[str],
    Sequence[ModelFieldMappingItem],
    Set[ModelFieldMappingItem],
]

MentionableImpl = TypeVar("MentionableImpl", bound=MentionableMixin)
