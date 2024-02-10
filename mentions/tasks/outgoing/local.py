import logging
from typing import Iterable, Optional, Set
from urllib.parse import urljoin

from bs4 import Tag
from django.core.exceptions import ValidationError

from mentions import config, options
from mentions.util import find_links_in_html, get_url_validator

__all__ = [
    "get_target_links_in_html",
    "is_valid_target",
]


log = logging.getLogger(__name__)


def get_target_links_in_html(
    html: str,
    source_path: str,
    allow_self_mentions: bool = options.allow_self_mentions(),
    domains_allow: Optional[Iterable[str]] = None,
    domains_deny: Optional[Iterable[str]] = None,
    domains_allow_tag: Optional[str] = options.outgoing_domains_tag_allow(),
    domains_deny_tag: Optional[str] = options.outgoing_domains_tag_deny(),
) -> Set[str]:
    """Get any links from `html` that should be treated as webmention targets.

    Links that use relative paths will be resolved to an absolute URL using
    `source_path` and `options.domain_name()`.

    Args:
        html: HTML-formatted text.
        source_path: The URL path of the HTML source, used to resolve absolute
                     URLs from any links that use relative paths.
        allow_self_mentions: See `options.allow_self_mentions`.
        domains_allow: See `options.outgoing_domains_allow`.
        domains_deny: See `options.outgoing_domains_deny`.
        domains_allow_tag: See `options.outgoing_domains_tag_allow`
        domains_deny_tag: See `options.outgoing_domains_tag_deny`
    Returns:
        Absolute URLs for any valid links from `html`.
    """
    domains_allow = domains_allow or options.outgoing_domains_allow()
    domains_deny = domains_deny or options.outgoing_domains_deny()
    valid_links = set()

    links = find_links_in_html(html)

    for link in links:
        href = link["href"]
        if href.startswith("#"):
            # Ignore local #anchors
            continue

        href = _resolve_relative_url(source_path, href)

        if _has_class_or_attribute(link, domains_deny_tag):
            continue

        if _has_class_or_attribute(link, domains_allow_tag):
            valid_links.add(href)
            continue

        if is_valid_target(
            href,
            allow_self_mentions,
            domains_allow=domains_allow,
            domains_deny=domains_deny,
        ):
            valid_links.add(href)

    return valid_links


def is_valid_target(
    url: str,
    allow_self_mention: bool,
    domains_allow: Optional[Iterable[str]],
    domains_deny: Optional[Iterable[str]],
) -> bool:
    """
    Args:
        url: The URL to be tested
        allow_self_mention: See `options.allow_self_mentions`.
        domains_allow: See `options.outgoing_domains_allow`.
        domains_deny: See `options.outgoing_domains_deny`.

    Returns:
        True if `url` is a valid URL and should be treated as a possible
        target for webmentions, otherwise False
    """
    try:
        validator = get_url_validator()
        validator(url)

    except ValidationError:
        return False

    return config.accept_domain_outgoing(
        url=url,
        allow_self_mention=allow_self_mention,
        domains_allow=domains_allow,
        domains_deny=domains_deny,
    )


def _resolve_relative_url(source_path: str, relative_path: str) -> str:
    return urljoin(urljoin(config.base_url(), source_path), relative_path)


def _has_class_or_attribute(tag: Tag, attr: str) -> bool:
    try:
        if attr in tag["class"]:
            return True
    except KeyError:
        pass

    if attr in tag.attrs:
        return True

    if f"data-{attr}" in tag.attrs:
        return True

    return False
