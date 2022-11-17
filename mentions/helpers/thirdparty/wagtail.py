import logging
from functools import partial
from typing import Callable, Optional, Type

from django.urls import ResolverMatch

from mentions.config import is_wagtail_installed
from mentions.exceptions import BadUrlConfig, NoModelForUrlPath, OptionalDependency
from mentions.helpers.resolution import get_model_for_url_by_helper
from mentions.helpers.types import MentionableImpl, ModelFieldMapping
from mentions.models.mixins import MentionableMixin

__all__ = [
    "mentions_wagtail_path",
    "mentions_wagtail_re_path",
    "get_model_for_url_by_wagtail",
]

try:
    from wagtail.contrib.routable_page.models import RoutablePageMixin, path, re_path
except ImportError:

    def config_error(name: str, *args, **kwargs):
        raise OptionalDependency(
            f"Helper '{name}' requires wagtail! "
            f"Maybe you meant to use the '{name.replace('wagtail_', '')}' "
            f"helper instead?"
        )

    path = lambda *args, **kwargs: config_error(
        "mentions_wagtail_path", *args, **kwargs
    )
    re_path = lambda *args, **kwargs: config_error(
        "mentions_wagtail_re_path", *args, **kwargs
    )

from django.apps import apps

from mentions import contract, options
from mentions.helpers.urls import get_dotted_model_name, get_lookup_from_urlpattern

log = logging.getLogger(__name__)


MENTIONS_KWARGS = "_mentions_kwargs"


def _path(
    wagtail_path_func: Callable,
    django_path_func: Callable,
    pattern: str,
    model_class: Type[MentionableImpl],
    model_field_mapping: Optional[ModelFieldMapping] = None,
    name: str = None,
):
    """Drop-in replacement for the Wagtail routable @path/@re_path decorators.

    Attach model lookup metadata directly to the view func, allowing us to
    resolve the correct Page instance.

    Args:
        wagtail_path_func: wagtail routable @path, @re_path
        django_path_func: django.urls path, re_path
        pattern: A URL pattern [passed to view func].
        model_class: The type of MentionableMixin model that this path represents.
        model_field_mapping: A mapping of captured kwarg names to model field names, if they differ.
            This may be a {captured_name: model_field_name} dictionary, or
            a list of (captured_name, model_field_name) tuples.
        name: Used for reverse lookup [passed to view func]
    """

    def decorator(view_func, *args, **kwargs):
        urlpattern = django_path_func(pattern, lambda: 0)
        lookup = (
            {contract.URLPATTERNS_MODEL_LOOKUP: model_field_mapping}
            if model_field_mapping
            else get_lookup_from_urlpattern(urlpattern)
        )

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


from django.urls import path as django_path
from django.urls import re_path as django_re_path

mentions_wagtail_path = partial(
    _path,
    path,
    django_path,
)
mentions_wagtail_re_path = partial(
    _path,
    re_path,
    django_re_path,
)


def get_model_for_url_by_wagtail(match: ResolverMatch) -> MentionableMixin:
    if not is_wagtail_installed():
        raise OptionalDependency("wagtail")

    import wagtail.views

    if match.func != wagtail.views.serve:
        raise OptionalDependency("wagtail")

    from wagtail.models.sites import get_site_for_hostname

    site = get_site_for_hostname(options.domain_name(), None)  # TODO get correct port
    path = match.args[0]
    path_components = [component for component in path.split("/") if component]

    page, args, kwargs = site.root_page.localized.specific.route(None, path_components)

    if isinstance(page, MentionableMixin):
        return page

    if not isinstance(page, RoutablePageMixin):
        raise NoModelForUrlPath()

    view_func, view_args, view_kwargs = args
    view_kwargs.update(view_func._mentions_kwargs)
    model_name = view_kwargs.get(contract.URLPATTERNS_MODEL_NAME)

    try:
        model_class: Type[MentionableMixin] = apps.get_model(model_name)

    except LookupError:
        raise BadUrlConfig(f"Cannot find model `{model_name}`!")

    return get_model_for_url_by_helper(model_class, view_kwargs)
