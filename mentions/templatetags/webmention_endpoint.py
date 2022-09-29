from django import template

from mentions.templatetags.webmentions import webmentions_endpoint

__all__ = [
    "webmentions_endpoint",
]

register = template.Library()


@register.simple_tag
def webmention_endpoint():
    """Deprecated: kept available here to avoid breaking change (for now)."""
    return webmentions_endpoint()
