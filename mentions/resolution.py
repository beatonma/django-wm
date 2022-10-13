import logging
from typing import List, Type

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.urls import Resolver404, ResolverMatch, get_resolver

from mentions import contract
from mentions.exceptions import BadUrlConfig, NoModelForUrlPath, TargetDoesNotExist
from mentions.helpers.resolution import get_model_for_url_by_helper
from mentions.models import SimpleMention, Webmention
from mentions.models.mixins import MentionableMixin, QuotableMixin
from mentions.util.url import get_urlpath

log = logging.getLogger(__name__)


__all__ = [
    "get_mentions_for_object",
    "get_mentions_for_view",
    "get_mentions_for_url",
    "get_model_for_url",
]


def get_urlpattern_match(url_path: str) -> ResolverMatch:
    """Resolves a URL path to the corresponding `urlpatterns` entry.

    Raises:
        TargetDoesNotExist: If a match cannot be found.
    """
    try:
        return get_resolver(settings.ROOT_URLCONF).resolve(url_path)
    except Resolver404:
        raise TargetDoesNotExist(
            f"Cannot find a matching urlpattern entry for path={url_path}"
        )


def get_model_for_url(url: str) -> MentionableMixin:
    """Find the model instance represented by the given URL.

    For this to work:
    - the `urlpatterns` entry that corresponds to the model must include
        a `model_name` kwarg with the model class' dotted path.
    - the model must implement the @classmethod `resolve_from_url_kwargs`

    For implementation details see:
     https://github.com/beatonma/django-wm/wiki/URL-Patterns
     https://github.com/beatonma/django-wm/wiki/Models#mentionablemixin

    e.g.
        path(
            r"articles/<int:article_id>/",
            ArticleView.as_view(),
            kwargs={
                "model_name": "blog.Article",
            },
            name="blog-article"),

    Returns:
        An instance of a model that implements MentionableMixin.

    Raises:
        TargetDoesNotExist: Unable to resolve `url_path` to a `ResolverMatch`,
            or a model instance cannot be resolved from ResolverMatch kwargs.
        NoModelForUrlPath: The ResolverMatch does not have `model_name` kwarg.
    """
    url_path = get_urlpath(url)
    match = get_urlpattern_match(url_path)
    urlpattern_kwargs = {**match.kwargs}

    try:
        model_name = urlpattern_kwargs.pop(contract.URLPATTERNS_MODEL_NAME)
    except KeyError:
        raise NoModelForUrlPath()

    try:
        model_class: Type[MentionableMixin] = apps.get_model(model_name)

    except LookupError:
        raise BadUrlConfig(
            f"Cannot find model `{model_name}` - check your urlpatterns!"
        )

    try:
        return get_model_for_url_by_helper(model_class, urlpattern_kwargs)

    except KeyError:
        # URL pattern was not created by helper functions.
        pass

    except ObjectDoesNotExist:
        raise TargetDoesNotExist(
            f"Cannot find instance of model `{model_class}` with kwargs=`{urlpattern_kwargs}`"
        )

    try:
        return model_class.resolve_from_url_kwargs(**urlpattern_kwargs)
    except ObjectDoesNotExist:
        raise TargetDoesNotExist(
            f"Cannot find instance of model `{model_class}` with kwargs=`{urlpattern_kwargs}`"
        )


def get_mentions_for_url(url: str) -> List[QuotableMixin]:
    try:
        obj = get_model_for_url(url)
        return obj.mentions()

    except NoModelForUrlPath:
        pass

    return get_public_mentions(target_url=url)


def get_mentions_for_view(request: HttpRequest) -> List[QuotableMixin]:
    return get_mentions_for_url(request.build_absolute_uri())


def get_mentions_for_object(obj: MentionableMixin) -> List[QuotableMixin]:
    ctype = ContentType.objects.get_for_model(obj.__class__)

    return get_public_mentions(content_type=ctype, object_id=obj.id)


def get_public_mentions(**filter) -> List[QuotableMixin]:
    webmentions = Webmention.objects.filter(
        **filter,
        approved=True,
        validated=True,
    )
    simple_mentions = SimpleMention.objects.filter(**filter)

    return list(webmentions) + list(simple_mentions)
