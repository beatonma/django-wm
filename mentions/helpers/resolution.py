from typing import Dict, Optional, Set, Tuple, Type, Union

from mentions import contract
from mentions.helpers.types import MentionableImpl, ModelFieldMapping


def get_model_for_url_by_helper(
    model_class: Type[MentionableImpl],
    urlpattern_kwargs: Dict,
) -> Optional[MentionableImpl]:
    """Resolve a model instance from urlpattern kwargs, as configured by
    `mentions_path` or `mentions_re_path` helper functions.

    Args:
        model_class: A class that inherits MentionableMixin.
        urlpattern_kwargs: kwargs from a `ResolverMatch`.

    Returns:
        An instance of `model_class`.

    Raises:
        KeyError: If the given urlpattern_kwargs does not contain helper values.
    """
    model_field_mapping: ModelFieldMapping = urlpattern_kwargs.pop(
        contract.URLPATTERNS_MODEL_LOOKUP
    )

    if isinstance(model_field_mapping, dict):
        model_field_mapping = set(model_field_mapping.items())

    def unpack_mapping(obj: Union[str, Tuple[str, str]]) -> Tuple[str, str]:
        # If mapping is a string, replace it with an 'identity' tuple of it: key == value.
        if isinstance(obj, str):
            return obj, obj
        return obj

    mapping: Set[Tuple[str, str]] = {unpack_mapping(x) for x in model_field_mapping}
    query = {value: urlpattern_kwargs[key] for key, value in mapping}

    return model_class.objects.get(**query)
