"""Utility functions used in multiple test files."""
import random
import uuid
from typing import Optional

from django.db import models
from django.urls import reverse

from mentions import config
from mentions.models import (
    HCard,
    OutgoingWebmentionStatus,
    PendingIncomingWebmention,
    PendingOutgoingContent,
    SimpleMention,
    Webmention,
)
from mentions.models.mixins import IncomingMentionType, MentionableMixin
from mentions.views import view_names
from tests.test_app.models import MentionableTestModel
from tests.tests.util import viewname


def create_mentionable_object(content: str = "", **kwargs):
    """Create and return an instance of MentionableTestModel."""
    return MentionableTestModel.objects.create(content=content, **kwargs)


def create_webmention(
    source_url: Optional[str] = None,
    target_url: Optional[str] = None,
    target_object: Optional[MentionableMixin] = None,
    post_type: Optional[IncomingMentionType] = None,
    sent_by: Optional[str] = None,
    approved: bool = True,
    validated: bool = True,
    has_been_read: bool = False,
    quote: Optional[str] = None,
    notes: Optional[str] = None,
    hcard: Optional[HCard] = None,
) -> Webmention:
    return Webmention.objects.create(
        source_url=source_url or random_url(),
        target_url=target_url or get_simple_url(),
        target_object=target_object,
        post_type=post_type.serialized_name() if post_type else None,
        sent_by=sent_by or random_url(),
        approved=approved,
        validated=validated,
        has_been_read=has_been_read,
        quote=quote or random_str(),
        notes=notes or random_url(),
        hcard=hcard,
    )


def create_simple_mention(
    source_url: Optional[str] = None,
    target_url: Optional[str] = None,
    target_object: Optional[MentionableMixin] = None,
    quote: Optional[str] = None,
) -> SimpleMention:
    return SimpleMention.objects.create(
        target_url=target_url or random_url(),
        source_url=source_url or random_url(),
        target_object=target_object,
        quote=quote or random_str(),
    )


def create_hcard(
    name: Optional[str] = None,
    homepage: Optional[str] = None,
    avatar: Optional[str] = None,
) -> HCard:
    return HCard.objects.create(
        name=name or random_str(),
        homepage=homepage or random_url(),
        avatar=avatar or random_url(),
    )


def create_outgoing_status(
    source_url: Optional[str] = None,
    target_url: Optional[str] = None,
    target_webmention_endpoint: Optional[str] = None,
    status_message: Optional[str] = None,
    response_code: Optional[int] = 200,
    successful: Optional[bool] = True,
) -> OutgoingWebmentionStatus:
    return OutgoingWebmentionStatus.objects.create(
        source_url=source_url or random_url(),
        target_url=target_url or random_url(),
        target_webmention_endpoint=target_webmention_endpoint or random_url(),
        status_message=status_message or random_str(),
        response_code=response_code,
        successful=successful,
    )


def create_pending_incoming(
    source_url: Optional[str] = None,
    target_url: Optional[str] = None,
    sent_by: Optional[str] = None,
) -> PendingIncomingWebmention:
    return PendingIncomingWebmention.objects.create(
        source_url=source_url or random_url(),
        target_url=target_url or get_simple_url(),
        sent_by=sent_by or random_url(),
    )


def create_pending_outgoing(
    absolute_url: Optional[str] = None,
    text: Optional[str] = None,
) -> PendingOutgoingContent:
    return PendingOutgoingContent.objects.create(
        absolute_url=absolute_url or random_url(),
        text=text or random_str(),
    )


def get_absolute_url_for_object(obj: models.Model = None):
    if obj is None:
        obj = create_mentionable_object(content=random_str())

    return config.build_url(obj.get_absolute_url())


def get_simple_url():
    """Return relative URL for a simple page with no associated models."""
    path = reverse(viewname.no_object_view)
    return config.build_url(path)


def endpoint_submit_webmention() -> str:
    """Return relative URL for our root webmention endpoint."""
    return reverse(view_names.webmention_api_incoming)


def endpoint_get_webmentions() -> str:
    """Return relative URL for our webmention /get endpoint."""
    return reverse(view_names.webmention_api_get)


def endpoint_get_webmentions_by_type() -> str:
    return reverse(view_names.webmention_api_get_by_type)


def endpoint_submit_webmention_absolute() -> str:
    """Return absolute URL for our root webmention endpoint on our domain."""
    return config.build_url(endpoint_submit_webmention())


def random_domain() -> str:
    """Return a randomised domain name."""
    return f"example-url-{random_str()}.org"


def random_url(
    scheme: Optional[str] = None,
    subdomain: Optional[str] = None,
    domain: Optional[str] = None,
    port: Optional[str] = None,
    path: Optional[str] = None,
) -> str:
    """Generate a random URL."""
    scheme = _take_not_null(scheme, random.choice(["http", "https"]))
    subdomain = _take_not_null(subdomain, random.choice(["", "", f"{random_str()}."]))
    domain = _take_not_null(domain, random_domain())
    port = _take_not_null(port, random.choice([""] * 5 + ["8000"]))
    if port:
        port = f":{port}"
    if path is None:
        path = "/".join([random_str() for _ in range(random.randint(0, 2))])
        path = path + random.choice(["", "/"])
    if len(path) > 0 and path[0] != "/":
        path = f"/{path}"

    return f"{scheme}://{subdomain}{domain}{port}{path}"


def random_str(length: int = 5) -> str:
    """Generate a short string of random characters."""
    return uuid.uuid4().hex[:length]


def mentions_model_classes():
    return [
        Webmention,
        OutgoingWebmentionStatus,
        PendingIncomingWebmention,
        PendingOutgoingContent,
        HCard,
        SimpleMention,
    ]


def _take_not_null(value, default):
    return value if value is not None else default
