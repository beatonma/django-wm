from functools import partial
from typing import Callable, Dict, Optional, Type

from django.urls import URLPattern, path, re_path

from mentions import contract
from mentions.helpers.types import MentionableImpl, ModelFieldMapping

__all__ = [
    "mentions_path",
    "mentions_re_path",
]


def _path(
    func: Callable,  # Either `django.urls.path` or `django.urls.re_path`.
    route: str,
    view: Callable,
    model_class: Type[MentionableImpl],
    model_field_mapping: Optional[ModelFieldMapping] = None,
    kwargs: Optional[Dict] = None,
    name: Optional[str] = None,
) -> URLPattern:
    """Proxy for `django.urls.path` and `django.urls.re_path` which enables simpler model resolution.

    This will add extra entries to given `kwargs` which enables model resolution
    via `get_model_for_url_by_helper`.

    Removes the need to implement `resolve_from_url_kwargs` on `model_class`.

    Args:
        route: A URL pattern [passed to func].
        view: A view function or the result of View.as_view() [passed to func].
        model_class: The type of MentionableMixin model that this path represents.
        model_field_mapping: A mapping of captured kwarg names to model field names, if they differ.
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
        kwargs=model_kwargs(
            model_class,
            model_field_mapping=model_field_mapping,
            kwargs=kwargs,
        ),
        name=name,
    )

    if model_field_mapping is None:
        inject_default_mapping(urlpattern)

    return urlpattern


mentions_path = partial(_path, path)
mentions_re_path = partial(_path, re_path)


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


def inject_default_mapping(urlpattern: URLPattern):
    default_mapping = urlpattern.pattern.converters.keys()
    urlpattern.default_args.update(
        {contract.URLPATTERNS_MODEL_LOOKUP: {name: name for name in default_mapping}}
    )
