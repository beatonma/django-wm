from typing import Dict, Optional, Sequence, Set, Tuple, Type

from mentions import contract
from mentions.helpers.types import (
    MentionableImpl,
    ModelFilter,
    ModelFilterMap,
    UrlKwarg,
)

__all__ = [
    "get_model_for_url_by_helper",
]

TypeSet = Set[Tuple[UrlKwarg, ModelFilter]]


def get_model_for_url_by_helper(
    model_class: Type[MentionableImpl],
    urlpattern_args: Sequence,
    urlpattern_kwargs: Dict,
) -> Optional[MentionableImpl]:
    """Resolve a model instance from urlpattern kwargs, as configured by
    `mentions_path` or `mentions_re_path` helper functions.

    Args:
        model_class: A class that inherits MentionableMixin.
        urlpattern_args: args from a `ResolverMatch`.
        urlpattern_kwargs: kwargs from a `ResolverMatch`.

    Returns:
        An instance of `model_class`.

    Raises:
        KeyError: If the given urlpattern_kwargs does not contain helper values.
    """

    model_filter_map: ModelFilterMap = urlpattern_kwargs.pop(
        contract.URLPATTERNS_MODEL_FILTER_MAP
    )

    mapping = unpack_model_filter_map(model_filter_map)
    query = {value: urlpattern_kwargs[key] for key, value in mapping}

    model_filters: Sequence = urlpattern_kwargs.pop(
        contract.URLPATTERNS_MODEL_FILTERS, []
    )
    for key, value in zip(model_filters, urlpattern_args):
        query[key] = value

    return model_class.objects.get(**query)


def unpack_model_filter_map(mapping: ModelFilterMap) -> TypeSet:
    if isinstance(mapping, dict):
        mapping = set(mapping.items())

    def unpack(item):
        # If mapping is a string, replace it with an 'identity' tuple of it: key == value.
        if isinstance(item, str):
            return item, item
        return item

    mapping = {unpack(x) for x in mapping}

    return mapping
