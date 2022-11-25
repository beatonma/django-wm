from typing import Dict, Set, Type

from django.urls import URLPattern

from mentions import contract
from mentions.helpers.types import MentionableImpl, SharedFieldName, UrlKwarg

__all__ = [
    "get_captured_filters",
    "get_dotted_model_name",
]


def get_dotted_model_name(model_class: Type[MentionableImpl]) -> str:
    model_app = model_class._meta.app_label
    model_name = model_class.__name__

    return f"{model_app}.{model_name}"


def get_captured_filters(
    urlpattern: URLPattern,
) -> Dict[UrlKwarg, Set[SharedFieldName]]:
    """Create default model_filter_map from captured parameters."""
    default_mapping = urlpattern.pattern.converters.keys()
    return {contract.URLPATTERNS_MODEL_FILTER_MAP: set(default_mapping)}
