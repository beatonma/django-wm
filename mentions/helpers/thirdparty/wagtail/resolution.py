from typing import Callable, Optional, Type

from django.apps import apps
from django.urls import ResolverMatch

from mentions import config, contract, options
from mentions.exceptions import BadUrlConfig, NoModelForUrlPath, OptionalDependency
from mentions.helpers.resolution import get_model_for_url_by_helper
from mentions.helpers.thirdparty.wagtail.proxy import RoutablePageMixin
from mentions.helpers.thirdparty.wagtail.util import get_annotation_from_viewfunc
from mentions.helpers.types import MentionableImpl, ModelClass
from mentions.models.mixins import MentionableMixin

__all__ = [
    "get_model_for_url_by_wagtail",
    "autopage_page_resolver",
]


def get_model_for_url_by_wagtail(match: ResolverMatch) -> MentionableMixin:
    """Try to resolve a Wagtail Page instance, if Wagtail is installed.

    If using RoutablePageMixin you must replace the Wagtail @path/@re_path
    decorators with @mentions_wagtail_path/@mentions_wagtail_re_path to add
    the metadata required to resolve the correct target Page.
    """

    if not config.is_wagtail_installed():
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

    kwarg_mapping = get_annotation_from_viewfunc(view_func)
    view_kwargs.update(kwarg_mapping)

    model_name = view_kwargs.get(contract.URLPATTERNS_MODEL_NAME)

    try:
        model_class: Type[MentionableMixin] = resolve_model(model_name, page)

    except LookupError:
        raise BadUrlConfig(f"Cannot find model `{model_name}`!")

    return get_model_for_url_by_helper(model_class, view_args, view_kwargs)


def autopage_page_resolver(
    model_class: ModelClass,
    lookup: dict,
    view_func: Callable,
) -> Callable:
    def wrapped_view_func(self, request, *args, **kwargs):
        resolved_model = resolve_model(model_class, view_func)
        lookup_kwargs = {**lookup, **kwargs}
        page = get_model_for_url_by_helper(resolved_model, args, lookup_kwargs)

        return view_func(self, request, page)

    return wrapped_view_func


def resolve_app_name(module_name: str) -> Optional[str]:
    app_configs = apps.get_app_configs()
    for conf in app_configs:
        if module_name.startswith(conf.name):
            return conf.label

    raise LookupError(f"Cannot find app for module {module_name}")


def resolve_model(model_class: ModelClass, context: object) -> Type[MentionableImpl]:
    """Resolve a model type from an identifier.

    model_class may be:
    - a class already.
    - a dotted string name for a class.
    - a simple class name. In this case, use context.__module__ to try and
      construct a valid dotted name for the class.
    """
    if not isinstance(model_class, str):
        return model_class

    if "." in model_class:
        return apps.get_model(model_class)

    app_name = resolve_app_name(context.__module__)
    return apps.get_model(f"{app_name}.{model_class}")
