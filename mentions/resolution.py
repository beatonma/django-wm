import logging
from importlib import import_module
from typing import Iterable, List, Optional, Type

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpRequest
from django.urls import Resolver404, ResolverMatch

from mentions.exceptions import BadConfig, TargetDoesNotExist
from mentions.models import HCard, OutgoingWebmentionStatus, SimpleMention, Webmention
from mentions.models.base import MentionsBaseModel
from mentions.models.mixins import MentionableMixin, QuotableMixin
from mentions.util import split_url

log = logging.getLogger(__name__)


__all__ = [
    "get_mentions_for_absolute_url",
    "get_mentions_for_object",
    "get_mentions_for_url_path",
    "get_mentions_for_view",
    "get_model_for_url_path",
    "get_or_create_outgoing_webmention",
    "update_or_create_hcard",
]


def _find_urlpattern(target_path: str) -> ResolverMatch:
    """
    Find a match in urlpatterns or raise TargetDoesNotExist
    """
    target_path = target_path.lstrip("/")  # Remove any leading slashes
    urlconf = import_module(settings.ROOT_URLCONF)
    urlpatterns = urlconf.urlpatterns

    for x in urlpatterns:
        # x may be an instance of either:
        # - django.urls.resolvers.URLResolver
        # - django.urls.resolvers.URLPattern
        try:
            match = x.resolve(target_path)
            if match:
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
    target_path: str,
    match: ResolverMatch = None,
) -> MentionableMixin:
    """
    Find a match in urlpatterns and return the corresponding model instance.

    Any mentionable View that corresponds to a model instance should include
    kwargs in its `urlpatterns` definition to enable resolution.
    - `model_name`: dotted python path for the target model.
    - Any other kwargs are passed to the model's `resolve_from_url_kwargs`
      classmethod to resolve the model instance. The default implementation
      uses the `slug` kwarg but this may be overridden.

        e.g.
        path(
            r"articles/<slug:slug>/",
            ArticleView.as_view(),
            kwargs={
                "model_name": "blog.Article",
            },
            name="blog-article"),
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
    match = _find_urlpattern(target_path)

    try:
        obj = get_model_for_url_path(target_path, match)
        return obj.mentions()
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


def get_mentions_for_object(obj: MentionableMixin) -> List[QuotableMixin]:
    ctype = ContentType.objects.get_for_model(obj.__class__)
    webmentions = Webmention.objects.filter(
        content_type=ctype,
        object_id=obj.id,
        approved=True,
        validated=True,
    )
    simple_mentions = SimpleMention.objects.filter(
        content_type=ctype,
        object_id=obj.id,
    )
    return list(webmentions) + list(simple_mentions)


def get_or_create_outgoing_webmention(
    source_urlpath: str,
    target_url: str,
    reset_retries: bool = False,
) -> OutgoingWebmentionStatus:
    """Safely get or create a OutgoingWebmentionStatus instance for given URLs.

    Since version 3.0.0 the URLs are effectively treated as 'unique together',
    but there may exist 'duplicate' instances from a previous installation."""

    kwargs = {
        "source_url": source_urlpath,
        "target_url": target_url,
    }
    try:
        status = OutgoingWebmentionStatus.objects.get_or_create(**kwargs)[0]
    except OutgoingWebmentionStatus.MultipleObjectsReturned:
        status = OutgoingWebmentionStatus.objects.filter(**kwargs).first()

    if reset_retries:
        status.reset_retries()

    return status


def update_or_create_hcard(
    homepage: Optional[str],
    name: Optional[str],
    avatar: Optional[str],
    data: str,
) -> HCard:
    """Any individual field may be used to create/retrieve an HCard.

    Ideally, homepage and name are used together.

    Otherwise, the order of precedence is [homepage, name, avatar].
    """

    if homepage and name:
        return _update_first_or_create(
            HCard,
            homepage=homepage,
            name=name,
            defaults={
                "avatar": avatar,
                "json": data,
            },
        )

    if homepage:
        return _update_first_or_create(
            HCard,
            homepage=homepage,
            name=None,
            defaults={
                "avatar": avatar,
                "json": data,
            },
        )

    if name:
        return _update_first_or_create(
            HCard,
            homepage=None,
            name=name,
            defaults={
                "avatar": avatar,
                "json": data,
            },
        )

    if avatar:
        return _update_first_or_create(
            HCard,
            homepage=None,
            name=None,
            avatar=avatar,
            defaults={
                "json": data,
            },
        )


def _update_first_or_create(
    model_cls: Type[MentionsBaseModel],
    defaults: dict,
    **query,
):
    try:
        return model_cls.objects.update_or_create(
            **query,
            defaults=defaults,
        )[0]

    except model_cls.MultipleObjectsReturned:
        instance = model_cls.objects.filter(**query).first()
        for key, value in defaults.items():
            setattr(instance, key, value)

        instance.save()
        return instance
