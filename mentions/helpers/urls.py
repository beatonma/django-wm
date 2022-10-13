from typing import Dict, Optional, Sequence, Type, Union

from django.urls import URLPattern, path, re_path

from mentions import contract
from mentions.util.types import MentionableImpl

__all__ = [
    "mentions_path",
    "mentions_re_path",
]


def mentions_path(
    route,
    view,
    model_class: Type[MentionableImpl],
    model_field_mapping: Optional[Union[Dict, Sequence]] = None,
    kwargs: Optional[Dict] = None,
    name: Optional[str] = None,
) -> URLPattern:
    """Proxy for `django.urls.path` which enables simpler model resolution.

    This will add extra entries to given `kwargs` which enables model resolution
    via `get_model_for_url_by_helper`.

    Removes the need to implement `resolve_from_url_kwargs` on `model_class`.

    Args:
        route: A URL pattern [passed to django.urls.path].
        view: A view function or the result of View.as_view() [passed to django.urls.path].
        model_class: The type of MentionableMixin model that this path represents.
        model_field_mapping: A mapping of captured kwarg names to model field names, if they differ.
            This may be a {captured_name: model_field_name} dictionary, or
            a list of (captured_name, model_field_name) pairs.
        kwargs: extras options for `view` [modified and passed to django.urls.path]
        name: Used for reverse lookup [passed to django.urls.path]

    Returns:
        A URLPattern with extra kwargs that enable resolving an instance of
        `model_class` from arguments captured from `route`.
    """
    return path(
        route,
        view,
        kwargs=model_kwargs(
            model_class,
            model_field_mapping=model_field_mapping,
            kwargs=kwargs,
        ),
        name=name,
    )


def mentions_re_path(
    route,
    view,
    model_class: Type[MentionableImpl],
    model_field_mapping: Optional[Union[Dict, Sequence]] = None,
    kwargs: Optional[Dict] = None,
    name: Optional[str] = None,
) -> URLPattern:
    """Proxy for `django.urls.re_path` which enables simpler model resolution.

    This will add extra entries to given `kwargs` which enables model resolution
    via `get_model_for_url_by_helper`.

    Removes the need to implement `resolve_from_url_kwargs` on `model_class`.

    Args:
        route: A URL pattern [passed to django.urls.re_path].
        view: A view function or the result of View.as_view() [passed to django.urls.re_path].
        model_class: The type of MentionableMixin model that this path represents.
        model_field_mapping: A mapping of captured kwarg names to model field names, if they differ.
            This may be a {captured_name: model_field_name} dictionary, or
            a list of (captured_name, model_field_name) pairs.
        kwargs: extras options for `view` [modified and passed to django.urls.re_path]
        name: Used for reverse lookup [passed to django.urls.re_path]

    Returns:
        A URLPattern with extra kwargs that enable resolving an instance of
        `model_class` from arguments captured from `route`.
    """
    return re_path(
        route,
        view,
        kwargs=model_kwargs(
            model_class,
            model_field_mapping=model_field_mapping,
            kwargs=kwargs,
        ),
        name=name,
    )


def get_dotted_model_name(model_class: Type[MentionableImpl]) -> str:
    model_app = model_class._meta.app_label
    model_name = model_class.__name__

    return f"{model_app}.{model_name}"


def model_kwargs(
    model_class: Type[MentionableImpl],
    model_field_mapping: Optional[Dict],
    kwargs: Optional[Dict],
) -> Dict:
    """Merge kwargs"""
    return {
        **(kwargs or {}),
        contract.URLPATTERNS_MODEL_NAME: get_dotted_model_name(model_class),
        contract.URLPATTERNS_MODEL_LOOKUP: model_field_mapping,
    }
