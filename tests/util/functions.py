"""
Utility functions used in multiple test files.
"""

import uuid

from django.utils.text import slugify

from . import constants


def get_id_and_slug():
    """Create a random id and slug for a MentionableTestModel."""
    _id = uuid.uuid4().hex[:6]
    slug = slugify(_id)
    return _id, slug


def url(path, slug=''):
    return f'/{constants.namespace}/{path}/{slug}'
