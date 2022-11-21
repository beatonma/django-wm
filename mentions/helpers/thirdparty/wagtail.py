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

        setattr(
            view_func,
            MENTIONS_KWARGS,
            {
                contract.URLPATTERNS_MODEL_NAME: get_dotted_model_name(model_class),
                **lookup,
            },
        )

        wagtail_result = wagtail_path_func(pattern, name=name)
        result = wagtail_result(view_func, *args, **kwargs)
        return result

    return decorator


def mentions_wagtail_path(
    pattern: str,
    model_class: Type[MentionableImpl],
    model_filter_map: Optional[ModelFilterMap] = None,
    name: str = None,
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
    """
    return _path(
        wagtail_path,
        django_path,
        pattern,
        model_class,
        None,
        model_filter_map,
        name,
    )


def mentions_wagtail_re_path(
    pattern: str,
    model_class: Type[MentionableImpl],
    model_filters: Optional[Sequence[ModelFilter]] = None,
    model_filter_map: Optional[ModelFilterMap] = None,
    name: str = None,
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
    """
    return _path(
        wagtail_re_path,
        django_re_path,
        pattern,
        model_class,
        model_filters,
        model_filter_map,
        name,
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
