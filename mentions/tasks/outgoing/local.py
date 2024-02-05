import logging
from typing import Iterable, List, Optional, Set
from urllib.parse import urljoin

from django.core.exceptions import ValidationError

from mentions import config, options
from mentions.util import find_links_in_html, get_domain, get_url_validator

__all__ = [
    "get_target_links_in_html",
    "is_valid_target",
]


log = logging.getLogger(__name__)


def get_target_links_in_html(
    html: str,
    source_path: str,
    allow_self_mentions: bool = options.allow_self_mentions(),
    included_domains: Optional[List[str]] = None,
    excluded_domains: Optional[List[str]] = None,
) -> Set[str]:
    """Get any links from `html` that should be treated as webmention targets.

    Links that use relative paths will be resolved to an absolute URL using
    `source_path` and `options.domain_name()`.

    If `options.allow_self_mentions()` is False, links that resolve to
    `options.domain_name()` will be ignored.

    Args:
        html: HTML-formatted text.
        source_path: The URL path of the HTML source, used to resolve absolute
                     URLs from any links that use relative paths.
        allow_self_mentions: See `options.allow_self_mentions`.
        included_domains: See `options.included_domains`.
        excluded_domains: See `options.excluded_domains`.

    Returns:
        Absolute URLs for any valid links from `html`.
    """
    included_domains = included_domains or options.included_domains()
    excluded_domains = excluded_domains or options.excluded_domains()
    valid_links = set()

    links = find_links_in_html(html)

    for link in links:
        href = link["href"]
        if href.startswith("#"):
            # Ignore local #anchors
            continue

        href = _resolve_relative_url(source_path, href)

        if is_valid_target(
            href,
            allow_self_mentions,
            included_domains=included_domains,
            excluded_domains=excluded_domains,
        ):
            valid_links.add(href)

    return valid_links


def is_valid_target(url: str, allow_self_mention: bool) -> bool:
def is_valid_target(
    url: str,
    allow_self_mention: bool,
    included_domains: Optional[Iterable[str]],
    excluded_domains: Optional[Iterable[str]],
) -> bool:
    """
    Args:
        url: The URL to be tested
        allow_self_mention: Whether this server should be allowed to send
            webmentions to itself.
        allow_self_mention: See `options.allow_self_mentions`.
        included_domains: See `options.included_domains`.
        excluded_domains: See `options.excluded_domains`.

    Returns:
        True if `url` is a valid URL and should be treated as a possible
        target for webmentions, otherwise False
    """
    try:
        validator = get_url_validator()
        validator(url)

    except ValidationError:
        return False

    domain = get_domain(url)

    if not allow_self_mention:
        if domain == options.domain_name():
            return False

    if excluded_domains:
        if domain in excluded_domains:
            return False
    if included_domains:
        if domain not in included_domains:
            return False

    return True


def _resolve_relative_url(source_path: str, relative_path: str) -> str:
    return urljoin(urljoin(config.base_url(), source_path), relative_path)
