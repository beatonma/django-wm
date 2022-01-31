"""
Utility functions used in multiple test files.
"""
import random
from typing import Tuple

from django.urls import reverse
from django.utils.text import slugify

from ..models import MentionableTestModel
from . import constants, viewname


def get_id_and_slug() -> Tuple[int, str]:
    """Create a random id and slug for a MentionableTestModel."""
    _id = random.randint(1, 1_000_000)
    slug = slugify(_id)
    return _id, slug


def url_path(path, slug=""):
    return f"/{path}/{slug}"


def get_mentioning_content(_url):
    """Return html content that links to the given url."""
    return f"""This is some content that mentions the target <a href="{_url}">url</a>"""


def build_object_url(slug):
    return (
        f"https://{constants.domain}{reverse(viewname.with_all_endpoints, args=[slug])}"
    )


def create_mentionable_objects(n: int = 3):
    """Create some arbitrary mentionable objects for noise."""

    for x in range(n):
        pk, slug = get_id_and_slug()
        MentionableTestModel.objects.create(pk=pk, slug=slug)
