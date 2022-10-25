import logging
from typing import Set
from urllib.parse import urljoin

from django.core.exceptions import ValidationError

from mentions import config, options
from mentions.util import find_links_in_html, get_domain, get_url_validator

__all__ = [
    "get_target_links_in_html",
    "is_valid_target",
]


log = logging.getLogger(__name__)


def get_target_links_in_html(html: str, source_path: str) -> Set[str]:
    """Get any links from `html` that should be treated as webmention targets.

    If `options.allow_self_mentions()` is `True`, links that use relative paths
    will be resolved to an absolute URL using `source_path` and
    `options.domain_name()`.

    Args:
        html: HTML-formatted text.
        source_path: The URL path of the HTML source, used to resolve absolute
                     URLs from any links that use relative paths.

    Returns:
        Absolute URLs for any valid links from `html`.
    """
    valid_links = set()
    allow_self_mentions = options.allow_self_mentions()

    for link in find_links_in_html(html):
        if is_valid_target(link, allow_self_mention=allow_self_mentions):
            valid_links.add(link)
            continue

        if "://" in link:
            # Ignore any unsupported schemes.
            continue

        if link.startswith("#"):
            # Ignore local #anchors
            continue

        if allow_self_mentions:
            abs_url = _path_to_absolute_url(link, source_path)
            if is_valid_target(abs_url, allow_self_mention=allow_self_mentions):
                valid_links.add(abs_url)
            else:
                log.warning(f"Constructed absolute url is invalid: {abs_url}")

    return valid_links


def is_valid_target(url: str, allow_self_mention: bool) -> bool:
    """

    Args:
        url: The URL to be tested
        allow_self_mention: Whether this server should be allowed to send
            webmentions to itself.

    Returns:
        True if `url` is a valid URL and should be treated as a possible
        target for webmentions, otherwise False
    """
    try:
        validator = get_url_validator()
        validator(url)

    except ValidationError:
        return False

    if not allow_self_mention:
        if get_domain(url) == options.domain_name():
            return False

    return True


def _path_to_absolute_url(relative_path: str, source_path: str) -> str:
    return urljoin(urljoin(config.base_url(), source_path), relative_path)
