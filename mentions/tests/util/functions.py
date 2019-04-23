"""
Utility functions used in multiple test files.
"""

import uuid

from django.utils.text import slugify
from django.urls import reverse

from . import constants


def get_id_and_slug():
    """Create a random id and slug for a MentionableTestModel."""
    _id = uuid.uuid4().hex[:6]
    slug = slugify(_id)
    return _id, slug


def url(path, slug=''):
    return f'/{constants.namespace}/{path}/{slug}'


def get_mentioning_content(_url):
    """Return html content that links to the given url."""
    return f'''This is some content that mentions the target <a href="{_url}">url</a>'''


def build_object_url(slug):
    return f'https://{constants.domain}{reverse(constants.view_all_endpoints, args=[slug])}'


def build_object_relative_url(slug):
    return reverse(constants.view_all_endpoints, args=[slug])