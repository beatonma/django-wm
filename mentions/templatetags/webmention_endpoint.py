from django import template
from django.urls import reverse
from django.utils.html import format_html

from mentions.views import view_names

register = template.Library()


@register.simple_tag
def webmention_endpoint():
    """Add your webmentions endpoint to your template <head>.

    e.g.
    {% load webmention_endpoint %}
    ...
    <head>
        {% webmention_endpoint %}
    </head>
    ...
    """
    endpoint = reverse(view_names.webmention_api_incoming)
    return format_html("""<link rel="webmention" href="{}" />""", endpoint)
