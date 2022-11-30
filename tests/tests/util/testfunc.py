"""Utility functions used in multiple test files."""
import random
import uuid
from typing import Optional

from django.db import models
from django.urls import reverse

from mentions import config
from mentions.models import Webmention
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
    quote: Optional[str] = None,
) -> Webmention:
    return Webmention.objects.create(
        source_url=source_url or random_url(),
        target_url=target_url or get_simple_url(),
        target_object=target_object,
        post_type=post_type.serialized_name() if post_type else None,
        sent_by=sent_by or random_url(),
        approved=approved,
        validated=validated,
        quote=quote,
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


def random_url() -> str:
    """Generate a random URL."""
    scheme = random.choice(["http", "https"])
    subdomain = random.choice(["", "", f"{random_str()}."])
    domain = random_domain()
    port = random.choice(([""] * 5) + [":8000"])
    path = "/".join([random_str() for _ in range(random.randint(0, 2))])
    path = (f"/{path}" if path else "") + random.choice(["", "/"])

    return f"{scheme}://{subdomain}{domain}{port}{path}"


def random_str(length: int = 5) -> str:
    """Generate a short string of random characters."""
    return uuid.uuid4().hex[:length]
