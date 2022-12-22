from typing import Callable, Dict, Optional, Sequence

from django.urls import URLPattern, path, re_path

from mentions import contract
from mentions.helpers.types import ModelClass, ModelFilter, ModelFilterMap
from mentions.helpers.util import get_captured_filters, get_dotted_model_name

__all__ = [
    "mentions_path",
    "mentions_re_path",
]


def _path(
    func: Callable,
    route: str,
    view: Callable,
    model_class: ModelClass,
    model_filters: Optional[Sequence[ModelFilter]],
    model_filter_map: Optional[ModelFilterMap],
    kwargs: Optional[Dict],
    name: Optional[str],
) -> URLPattern:
    """Proxy for `django.urls.path` and `django.urls.re_path` which enables simpler model resolution.

    This will add extra entries to given `kwargs` which enables model resolution
    via `get_model_for_url_by_helper`.

    Removes the need to implement `resolve_from_url_kwargs` on `model_class`.

    Args:
        func: Either `django.urls.path` or `django.urls.re_path`.
        route: URL pattern [passed to func].
        view: A view function or the result of View.as_view() [passed to func].
        model_class: The type of MentionableMixin model that this path represents.
        model_filters: (re_path only) An ordered list of model field names which
            are represented by unnamed groups in the regex pattern.
        model_filter_map: A mapping of captured kwarg names to model field names, if they differ.
            This may be a {captured_name: model_field_name} dictionary, or
            a list of (captured_name, model_field_name) tuples.
        kwargs: extras options for `view` [modified and passed to func]
        name: Used for reverse lookup [passed to func]

    Returns:
        A URLPattern with extra kwargs that enable resolving an instance of
        `model_class` from arguments captured from `route`.
    """
    urlpattern: URLPattern = func(
        route,
        view,
        kwargs=build_model_kwargs(
            model_class,
            model_filters=model_filters,
            model_filter_map=model_filter_map,
            kwargs=kwargs,
        ),
        name=name,
    )

    if model_filter_map is None:
        # Use captured params for object resolution if no custom mapping provided.
        urlpattern.default_args.update(get_captured_filters(urlpattern))

    return urlpattern


def mentions_path(
    route: str,
    view: Callable,
    model_class: ModelClass,
    model_filter_map: Optional[ModelFilterMap] = None,
    kwargs: Optional[Dict] = None,
    name: Optional[str] = None,
):
    """Proxy for `django.urls.path` to enable MentionableMixin model resolution.

    This will add extra entries to given `kwargs` which enables model resolution
    via `get_model_for_url_by_helper`.

    Removes the need to implement `resolve_from_url_kwargs` on `model_class`.

    Args:
        route: URL pattern.
        view: A view function or the result of View.as_view() [passed to func].
        model_class: The type of MentionableMixin model that this path represents.
        model_filter_map: A mapping of captured kwarg names to model field names, if they differ.
            This may be a {captured_name: model_field_name} dictionary, or
            a list of (captured_name, model_field_name) tuples.
        kwargs: extras options for `view`.
        name: Used for reverse lookup.

    Returns:
        A URLPattern with extra kwargs that enable resolving an instance of
        `model_class` from arguments captured from `route`.
    """
    return _path(
        path,
        route=route,
        view=view,
        model_class=model_class,
        model_filters=None,
        model_filter_map=model_filter_map,
        kwargs=kwargs,
        name=name,
    )


def mentions_re_path(
    route: str,
    view: Callable,
    model_class: ModelClass,
    model_filters: Optional[Sequence[ModelFilter]] = None,
    model_filter_map: Optional[ModelFilterMap] = None,
    kwargs: Optional[Dict] = None,
    name: Optional[str] = None,
):
    """Proxy for `django.urls.re_path` to enable MentionableMixin model resolution.

    This will add extra entries to given `kwargs` which enables model resolution
    via `get_model_for_url_by_helper`.

    Removes the need to implement `resolve_from_url_kwargs` on `model_class`.

    Args:
        route: URL pattern.
        view: A view function or the result of View.as_view() [passed to func].
        model_class: The type of MentionableMixin model that this path represents.
        model_filters: An ordered list of model field names which
            are represented by unnamed groups in the regex pattern.
        model_filter_map: A mapping of captured kwarg names to model field names, if they differ.
            This may be a {captured_name: model_field_name} dictionary, or
            a list of (captured_name, model_field_name) tuples.
        kwargs: extras options for `view`.
        name: Used for reverse lookup.

    Returns:
        A URLPattern with extra kwargs that enable resolving an instance of
        `model_class` from arguments captured from `route`.
    """
    return _path(
        re_path,
        route=route,
        view=view,
        model_class=model_class,
        model_filters=model_filters,
        model_filter_map=model_filter_map,
        kwargs=kwargs,
        name=name,
    )


def build_model_kwargs(
    model_class: ModelClass,
    model_filters: Optional[Sequence[ModelFilter]],
    model_filter_map: Optional[Dict],
    kwargs: Optional[Dict],
) -> Dict:
    """Merge kwargs"""
    fields = (
        {contract.URLPATTERNS_MODEL_FILTERS: model_filters} if model_filters else {}
    )

    return {
        **(kwargs or {}),
        contract.URLPATTERNS_MODEL_NAME: get_dotted_model_name(model_class),
        contract.URLPATTERNS_MODEL_FILTER_MAP: model_filter_map,
        **fields,
    }
