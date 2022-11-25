import logging

from django import template
from django.urls import reverse
from django.utils.html import format_html

from mentions import options, permissions
from mentions.views import view_names

__all__ = [
    "webmentions_dashboard",
    "webmentions_endpoint",
]

log = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag(takes_context=True)
def webmentions_dashboard(context: dict, link_text: str = "Webmentions Dashboard"):
    """Add a customisable link to your webmentions dashboard in a template."""

    has_permission = context["perms"]["mentions"][
        permissions.can_view_dashboard.codename
    ]
    if not has_permission and not options.dashboard_public():
        return ""

    url = reverse(view_names.webmention_dashboard)
    return format_html(
        """<a href="{url}">{link_text}</a>""",
        url=url,
        link_text=link_text,
    )


@register.simple_tag
def webmentions_endpoint():
    """Add your webmentions endpoint <link> to your template <head>.

    e.g.
    {% load webmentions %}
    ...
    <head>
        {% webmentions_endpoint %}
    </head>
    ...
    """
    endpoint = reverse(view_names.webmention_api_incoming)
    return format_html(
        """<link rel="webmention" href="{endpoint}" />""",
        endpoint=endpoint,
    )
