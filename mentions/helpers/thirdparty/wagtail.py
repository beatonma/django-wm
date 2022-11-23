import logging
from typing import Callable, Optional, Sequence, Type

from django.apps import apps
from django.urls import ResolverMatch, URLPattern
from django.urls import path as django_path
from django.urls import re_path as django_re_path

from mentions import contract, options
from mentions.config import is_wagtail_installed
from mentions.exceptions import BadUrlConfig, NoModelForUrlPath, OptionalDependency
from mentions.helpers.resolution import get_model_for_url_by_helper
from mentions.helpers.types import MentionableImpl, ModelFilter, ModelFilterMap
from mentions.helpers.urls import get_dotted_model_name, get_lookup_from_urlpattern
from mentions.models.mixins import MentionableMixin

try:
    from wagtail.contrib.routable_page.models import RoutablePageMixin
    from wagtail.contrib.routable_page.models import path as wagtail_path
    from wagtail.contrib.routable_page.models import re_path as wagtail_re_path
except ImportError:

    def config_error(name: str, *args, **kwargs):
        raise OptionalDependency(
            f"Helper '{name}' requires wagtail! "
            f"Maybe you meant to use the '{name.replace('wagtail_', '')}' "
            f"helper instead?"
        )

    wagtail_path = lambda *args, **kwargs: config_error(
        "mentions_wagtail_path", *args, **kwargs
    )
    wagtail_re_path = lambda *args, **kwargs: config_error(
        "mentions_wagtail_re_path", *args, **kwargs
    )


__all__ = [
    "mentions_wagtail_path",
    "mentions_wagtail_re_path",
    "get_model_for_url_by_wagtail",
]

log = logging.getLogger(__name__)


MENTIONS_KWARGS = "_mentions_kwargs"


def _path(
    wagtail_path_func: Callable,
    django_path_func: Callable,
    pattern: str,
    model_class: Type[MentionableImpl],
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
            - Completely replaces the args+kwargs of the view function which may be confusing.
                The resulting view function will have the signature `def func(self, request, page)`.
                This is an intentional restriction to make sure this is only used for simple cases.
    """

    def decorator(view_func, *args, **kwargs):
        urlpattern: URLPattern = django_path_func(
            pattern,
            lambda: 0,  # fake View
        )

        lookup = (
            {contract.URLPATTERNS_MODEL_FILTER_MAP: model_filter_map}
            if model_filter_map
            else get_lookup_from_urlpattern(urlpattern)
        )

        if model_filters:
            lookup[contract.URLPATTERNS_MODEL_FILTERS] = model_filters

        wagtail_path = wagtail_path_func(pattern, name=name)

        if autopage:
            view_func = autopage_page_resolver(model_class, lookup, view_func)

        setattr(
            view_func,
            MENTIONS_KWARGS,
            {
                contract.URLPATTERNS_MODEL_NAME: get_dotted_model_name(model_class),
                **lookup,
            },
        )

        path = wagtail_path(view_func, *args, **kwargs)

        return path

    return decorator


def mentions_wagtail_path(
    pattern: str,
    model_class: Type[MentionableImpl],
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
            - Completely replaces the args+kwargs of the view function which may be confusing.
                The resulting view function will have the signature `def func(self, request, page)`.
                This is an intentional restriction to make sure this is only used for simple cases.
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
    model_class: Type[MentionableImpl],
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
            - Completely replaces the args+kwargs of the view function which may be confusing.
                The resulting view function will have the signature `def func(self, request, page)`.
                This is an intentional restriction to make sure this is only used for simple cases.
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


def get_model_for_url_by_wagtail(match: ResolverMatch) -> MentionableMixin:
    """Try to resolve a Wagtail Page instance, if Wagtail is installed.

    If using RoutablePageMixin you must replace the Wagtail @path/@re_path
    decorators with @mentions_wagtail_path/@mentions_wagtail_re_path to add
    the metadata required to resolve the correct target Page.
    """

    if not is_wagtail_installed():
        raise OptionalDependency("wagtail")

    import wagtail.views

    if match.func != wagtail.views.serve:
        raise OptionalDependency("wagtail")

    from wagtail.models.sites import get_site_for_hostname

    site = get_site_for_hostname(options.domain_name(), None)
    path = match.args[0]
    path_components = [component for component in path.split("/") if component]

    page, args, kwargs = site.root_page.localized.specific.route(None, path_components)

    if isinstance(page, MentionableMixin):
        return page

    if not isinstance(page, RoutablePageMixin):
        raise NoModelForUrlPath()

    view_func, view_args, view_kwargs = args

    kwarg_mapping = getattr(view_func, MENTIONS_KWARGS, {})
    view_kwargs.update(kwarg_mapping)

    model_name = view_kwargs.get(contract.URLPATTERNS_MODEL_NAME)

    try:
        model_class: Type[MentionableMixin] = apps.get_model(model_name)

    except LookupError:
        raise BadUrlConfig(f"Cannot find model `{model_name}`!")

    return get_model_for_url_by_helper(model_class, view_args, view_kwargs)


def autopage_page_resolver(
    model_class: Type[MentionableImpl],
    lookup: dict,
    view_func: Callable,
) -> Callable:
    def wrapped_view_func(self, request, *args, **kwargs):
        lookup_kwargs = {**lookup, **kwargs}
        page = get_model_for_url_by_helper(model_class, args, lookup_kwargs)

        return view_func(self, request, page)

    return wrapped_view_func
