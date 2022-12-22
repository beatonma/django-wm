from typing import Dict, Sequence, Tuple, Type, TypeVar, Union

from mentions.models.mixins import MentionableMixin

"""Represents the name of a captured group from a URL pattern."""
UrlKwarg = str

"""Represents the name of a filter that can be used in a Django query.

This may simply be a field name like `title`, or something more complex 
like `date__year`, although Q and F objects are not currently supported."""
ModelFilter = str


"""A name that represents a UrlKwarg AND a ModelFilter.

The same name is used in the URL pattern and the resulting database query."""
SharedFieldName = str

ModelFilterMap = Union[
    Dict[UrlKwarg, ModelFilter],
    Sequence[SharedFieldName],
    Sequence[Tuple[UrlKwarg, ModelFilter]],
]

MentionableImpl = TypeVar("MentionableImpl", bound=MentionableMixin)
ModelClass = Union[Type[MentionableImpl], str]
