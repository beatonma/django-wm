import logging
from importlib import import_module
from typing import Iterable, List, Type

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpRequest
from django.urls import Resolver404, ResolverMatch

from mentions.exceptions import BadConfig, TargetDoesNotExist
from mentions.models import QuotableMixin, SimpleMention, Webmention
from mentions.util import split_url

log = logging.getLogger(__name__)


def _find_urlpattern(target_path: str) -> ResolverMatch:
    """
    Find a match in urlpatterns or raise TargetDoesNotExist
    """
    target_path = target_path.lstrip("/")  # Remove any leading slashes
    urlconf = import_module(settings.ROOT_URLCONF)
    urlpatterns = urlconf.urlpatterns

    try:
        from django.contrib.flatpages.views import flatpage
    except ImportError:
        flatpage = None

    for x in urlpatterns:
        # x may be an instance of either:
        # - django.urls.resolvers.URLResolver
        # - django.urls.resolvers.URLPattern
        try:
            match = x.resolve(target_path)
            if match:
                if flatpage and match.func != flatpage:
                    break
                else:
                    break
        except Resolver404:
            # May be raised by URLResolver
            pass
    else:
        # No match found
        raise TargetDoesNotExist(
            f"Cannot find a matching urlpattern entry for path={target_path}"
        )
    log.debug(f"Found matching urlpattern: {match}")
    return match


def get_model_for_url_path(
    target_path: str, match: ResolverMatch = None
) -> Type["MentionableMixin"]:
    """
    Find a match in urlpatterns and return the corresponding model instance.
    """
    if match is None:
        match = _find_urlpattern(target_path)

    urlpath_kwargs: dict = dict(**match.kwargs)

    # Dotted path to model class declaration
    try:
        model_name = urlpath_kwargs.pop("model_name")
    except KeyError:
        raise BadConfig(
            f"urlpattern must include a kwargs entry called 'model_name': {match}"
        )

    try:
        model = apps.get_model(model_name)
    except LookupError:
        raise BadConfig(f"Cannot find model `{model_name}` - check your urlpattern!")

    try:
        return model.resolve_from_url_kwargs(**urlpath_kwargs)
    except ObjectDoesNotExist:
        raise TargetDoesNotExist(
            f"Cannot find instance of model='{model}' with kwargs='{urlpath_kwargs}'"
        )


def get_mentions_for_url_path(
    target_path: str,
    full_target_url: str,
) -> List[QuotableMixin]:
    """If target_path resolves to a page associated with a MentionableMixin model"""
    match = _find_urlpattern(target_path)

    try:
        obj = get_model_for_url_path(target_path, match)
        return obj.mentions
    except (BadConfig, TargetDoesNotExist):
        pass

    # Add or remove a trailing slash to full_target_url so we can look for both.
    full_target_url_invert_slash = (
        full_target_url[:-1] if full_target_url.endswith("/") else f"{full_target_url}/"
    )

    q_filter = (
        Q(target_url=full_target_url)
        | Q(target_url=full_target_url_invert_slash)
        | Q(target_url=target_path)
    )

    webmentions = Webmention.objects.filter(
        q_filter,
        approved=True,
        validated=True,
    )
    simple_mentions = SimpleMention.objects.filter(q_filter)

    return list(webmentions) + list(simple_mentions)


def get_mentions_for_absolute_url(url: str) -> Iterable[QuotableMixin]:
    scheme, domain, path = split_url(url)
    full_target_url = f"{scheme}://{domain}{path}"

    return get_mentions_for_url_path(path, full_target_url=full_target_url)


def get_mentions_for_view(request: HttpRequest) -> Iterable[QuotableMixin]:
    """Call from your View implementation so you can include mentions in your template."""

    return get_mentions_for_absolute_url(request.build_absolute_uri())
