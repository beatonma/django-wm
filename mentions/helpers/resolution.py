from typing import Dict, Optional, Type

from mentions import contract
from mentions.models.mixins import MentionableMixin
from mentions.util.types import MentionableImpl


def get_model_for_url_by_helper(
    model_class: Type[MentionableImpl],
    urlpattern_kwargs: Dict,
) -> Optional[MentionableMixin]:
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
    model_field_mapping = urlpattern_kwargs.pop(contract.URLPATTERNS_MODEL_LOOKUP)

    if isinstance(model_field_mapping, dict):
        model_field_mapping = model_field_mapping.items()

    query = {value: urlpattern_kwargs[key] for key, value in model_field_mapping}
    return model_class.objects.get(**query)
