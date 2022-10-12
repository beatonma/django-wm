import random

from django import template
from django.utils.safestring import mark_safe

from mentions import config

register = template.Library()


@register.simple_tag()
def maybe_link_hcard(name: str):
    if random.random() > 0.67:
        return mark_safe(
            f"""<a class="p-author h-card" href="{config.base_url()}">{name}</a>"""
        )

    return mark_safe(f"""<span class="p-author h-card">{name}</span<""")
