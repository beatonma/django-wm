import logging
from typing import Iterable, List, Optional, Set
from urllib.parse import urljoin

from bs4 import Tag
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
    allow_domains: Optional[List[str]] = None,
    deny_domains: Optional[List[str]] = None,
    domain_override_attr: Optional[str] = options.outgoing_domains_override_attr(),
) -> Set[str]:
    """Get any links from `html` that should be treated as webmention targets.

    Links that use relative paths will be resolved to an absolute URL using
    `source_path` and `options.domain_name()`.

    Args:
        html: HTML-formatted text.
        source_path: The URL path of the HTML source, used to resolve absolute
                     URLs from any links that use relative paths.
        allow_self_mentions: See `options.allow_self_mentions`.
        allow_domains: See `options.outgoing_domains_allow`.
        deny_domains: See `options.outgoing_domains_deny`.
        domain_override_attr: See `options.outgoing_domains_override_attr`
    Returns:
        Absolute URLs for any valid links from `html`.
    """
    allow_domains = allow_domains or options.outgoing_domains_allow()
    deny_domains = deny_domains or options.outgoing_domains_deny()
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
            allow_domains=allow_domains,
            deny_domains=deny_domains,
            override_include_exclude=_has_class_or_attribute(
                tag=link,
                attr=domain_override_attr,
            ),
        ):
            valid_links.add(href)

    return valid_links


def is_valid_target(
    url: str,
    allow_self_mention: bool,
    allow_domains: Optional[Iterable[str]],
    deny_domains: Optional[Iterable[str]],
    override_include_exclude: bool = False,
) -> bool:
    """
    Args:
        url: The URL to be tested
        allow_self_mention: See `options.allow_self_mentions`.
        allow_domains: See `options.outgoing_domains_allow`.
        deny_domains: See `options.outgoing_domains_deny`.
        override_include_exclude: See `options.domains_override_attr`

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

    if not allow_self_mention and domain == options.domain_name():
        return False

    if deny_domains:
        if override_include_exclude:
            return True
        if domain in deny_domains:
            return False

    if allow_domains:
        if override_include_exclude:
            return False
        if domain not in allow_domains:
            return False

    return True


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
