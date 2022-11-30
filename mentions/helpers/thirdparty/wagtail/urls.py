import logging
from typing import Callable, Optional, Sequence

from django.urls import URLPattern
from django.urls import path as django_path
from django.urls import re_path as django_re_path

from mentions import contract
from mentions.helpers.thirdparty.wagtail.proxy import wagtail_path, wagtail_re_path
from mentions.helpers.thirdparty.wagtail.resolution import autopage_page_resolver
from mentions.helpers.thirdparty.wagtail.util import annotate_viewfunc
from mentions.helpers.types import ModelClass, ModelFilter, ModelFilterMap
from mentions.helpers.util import get_captured_filters

__all__ = [
    "mentions_wagtail_path",
    "mentions_wagtail_re_path",
    "mentions_wagtail_route",
]

log = logging.getLogger(__name__)


def _path(
    wagtail_path_func: Callable,
    django_path_func: Callable,
    pattern: str,
    model_class: ModelClass,
    model_filters: Optional[Sequence[str]],
    model_filter_map: Optional[ModelFilterMap],
    name: Optional[str],
    autopage: bool,
):
    """Drop-in replacement for the Wagtail routable @path/@re_path decorators.

    Attach model lookup metadata directly to the view func, allowing us to
    resolve the correct Page instance.

    Args:
        wagtail_path_func: wagtail routable @path, @re_path
        django_path_func: django.urls path, re_path
        pattern: A URL pattern [passed to view func].
        model_class: The type of MentionableMixin model that this path represents.
        model_filters: (re_path only) An ordered list of model field names which
            are represented by unnamed groups in the regex pattern.
        model_filter_map: A mapping of captured kwarg names to model field names, if they differ.
            This may be a {captured_name: model_field_name} dictionary, or
            a list of (captured_name, model_field_name) tuples.
        name: Used for reverse lookup [passed to view func]
        autopage: Use with care! Handy but likely controversial.
            If True, automatically resolve the target page and pass it to the view_func.
            - Reduces boilerplate when defining views as you don't have to define
                the same query twice (decorator + view func).
            - The resulting view function will have the signature `def func(self, request, page)`,
              with no additional args or kwargs allowed. This is an intentional restriction to make
              sure this is only used for simple cases.
    """

    def decorator(view_func, *args, **kwargs):
        urlpattern: URLPattern = django_path_func(
            pattern,
            lambda: 0,  # fake View
        )

        lookup = (
            {contract.URLPATTERNS_MODEL_FILTER_MAP: model_filter_map}
            if model_filter_map
            else get_captured_filters(urlpattern)
        )

        if model_filters:
            lookup[contract.URLPATTERNS_MODEL_FILTERS] = model_filters

        wagtail_path = wagtail_path_func(pattern, name=name)

        if autopage:
            view_func = autopage_page_resolver(model_class, lookup, view_func)

        view_func = annotate_viewfunc(view_func, model_class, lookup)
        path = wagtail_path(view_func, *args, **kwargs)

        return path

    return decorator


def mentions_wagtail_path(
    pattern: str,
    model_class: ModelClass,
    model_filter_map: Optional[ModelFilterMap] = None,
    name: str = None,
    autopage=False,
):
    """Drop-in replacement for the Wagtail routable @path decorator.

    Attach model lookup metadata directly to the view func, allowing us to
    resolve the correct Page instance.

    Args:
        pattern: A URL pattern [passed to view func].
        model_class: The type of MentionableMixin model that this path represents.
        model_filter_map: A mapping of captured kwarg names to model field names, if they differ.
            This may be a {captured_name: model_field_name} dictionary, or
            a list of (captured_name, model_field_name) tuples.
        name: Used for reverse lookup [passed to view func]
        autopage: Use with care! Handy but likely controversial.
            Default False.
            If True, automatically resolve the target page and pass it to the view_func.
            - Reduces boilerplate when defining views as you don't have to define
                the same query twice (decorator + view func).
            - The resulting view function will have the signature `def func(self, request, page)`,
              with no additional args or kwargs allowed. This is an intentional restriction to make
              sure this is only used for simple cases.
    """
    return _path(
        wagtail_path_func=wagtail_path,
        django_path_func=django_path,
        pattern=pattern,
        model_class=model_class,
        model_filters=None,
        model_filter_map=model_filter_map,
        name=name,
        autopage=autopage,
    )


def mentions_wagtail_re_path(
    pattern: str,
    model_class: ModelClass,
    model_filters: Optional[Sequence[ModelFilter]] = None,
    model_filter_map: Optional[ModelFilterMap] = None,
    name: str = None,
    autopage=False,
):
    """Drop-in replacement for the Wagtail routable @re_path decorator.

    Attach model lookup metadata directly to the view func, allowing us to
    resolve the correct Page instance.

    As with the core Django equivalent `re_path`, regex may use either named or
    unnamed groups but not both.

    Args:
        pattern: A regex URL pattern [passed to view func].
        model_class: The type of MentionableMixin model that this path represents.
        model_filters: An ordered list of model field names which are represented
            by unnamed groups in the regex pattern.
        model_filter_map: A mapping of captured group names to model field
            names, if they differ. This may be a {captured_name: model_field_name}
            dictionary, or a sequence of (captured_name, model_field_name) tuples.
        name: Used for reverse lookup [passed to view func]
        autopage: Use with care! Handy but likely controversial.
            Default False.
            If True, automatically resolve the target page and pass it to the view_func.
            - Reduces boilerplate when defining views as you don't have to define
                the same query twice (decorator + view func).
            - The resulting view function will have the signature `def func(self, request, page)`,
              with no additional args or kwargs allowed. This is an intentional restriction to make
              sure this is only used for simple cases.
    """
    return _path(
        wagtail_path_func=wagtail_re_path,
        django_path_func=django_re_path,
        pattern=pattern,
        model_class=model_class,
        model_filters=model_filters,
        model_filter_map=model_filter_map,
        name=name,
        autopage=autopage,
    )


mentions_wagtail_route = mentions_wagtail_re_path
