"""
Utility functions used in multiple test files.
"""
import random
import uuid
from typing import Tuple

from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify

from mentions.views import view_names

from . import viewname


def get_id_and_slug() -> Tuple[int, str]:
    """Create a random id and slug for a MentionableTestModel."""
    _id = random.randint(1, 1_000_000)
    slug = slugify(_id)
    return _id, slug


def get_url(slug):
    """Return the absolute URL for the target slug on our domain."""
    return f"https://{settings.DOMAIN_NAME}{get_urlpath(slug)}"


def get_urlpath(slug: str) -> str:
    """Return the relative URL for the target slug."""
    return reverse(viewname.with_all_endpoints, args=[slug])


def endpoint_submit_webmention() -> str:  #
    """Return relative URL for our root webmention endpoint."""
    return reverse(view_names.webmention_api_incoming)


def endpoint_get_webmentions() -> str:
    """Return relative URL for our webmention /get endpoint."""
    return reverse(view_names.webmention_api_get_for_object)


def endpoint_submit_webmention_absolute() -> str:
    """Return absolute URL for our root webmention endpoint on our domain."""
    return f"https://{settings.DOMAIN_NAME}{endpoint_submit_webmention()}"


def random_domain() -> str:
    """Return a randomised domain name."""
    return f"example-url-{uuid.uuid4().hex[:5]}.org"
