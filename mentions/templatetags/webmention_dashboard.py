import re

from django import template
from django.conf import settings
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


__all__ = [
    "arrow_icon",
    "more_icon",
    "success_icon",
    "short_url",
]


@register.simple_tag
def success_icon(successful: bool) -> str:
    successful_str = mark_safe(str(successful).lower())

    if successful:
        title = "Success"
        icon = mark_safe("&check;")

    else:
        title = "Failed"
        icon = mark_safe("&#10539;")

    return format_html(
        """<span class="icon" data-successful="{successful_str}" title="{title}">{icon}</span>""",
        successful_str=successful_str,
        title=title,
        icon=icon,
    )


@register.simple_tag
def short_url(url: str) -> str:
    max_length = 24
    is_self_url = False

    url = re.sub("https?://", "", url)

    if url.startswith("/"):
        is_self_url = True
    else:
        own_hosts = settings.ALLOWED_HOSTS
        for host in own_hosts:
            if url.startswith(host):
                url = url.replace(host, "")
                is_self_url = True
                break

    if len(url) > max_length:
        url = f"{url[:int(max_length / 3)]}…{url[int(max_length * 2 / 3):]}"

    if is_self_url:
        # Replace own domain with 'home' icon for brevity.
        return format_html("""<span class="icon">&#127968;</span>{url}""", url=url)

    return mark_safe(url)


@register.simple_tag
def arrow_icon() -> str:
    return mark_safe("""<span class="icon">&rarr;</span>""")


@register.simple_tag
def more_icon() -> str:
    return mark_safe(
        """<span class="icon" data-icon="more" title="Click to show detail">&vellip;</span>"""
    )
