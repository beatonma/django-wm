"""Helper functions that derive from `mentions.options` values."""
import logging
from typing import Optional, Set
from urllib.parse import urljoin

from mentions import options
from mentions.util import compatibility, get_domain

log = logging.getLogger(__name__)


def base_url() -> str:
    """Get the base URL of this server from current `options`."""
    return f"{options.url_scheme()}://{options.domain_name()}"


def build_url(path: str) -> str:
    """Construct an absolute URL for the given path on this server."""
    return urljoin(base_url(), path)


def is_wagtail_installed() -> bool:
    from importlib.util import find_spec

    wagtail_spec = find_spec("wagtail")
    return wagtail_spec is not None


def accept_domain_incoming(
    url: str,
    domains_allow: Optional[Set[str]],
    domains_deny: Optional[Set[str]],
) -> bool:
    """Determine whether the current options allow us to accept webmentions from the given URL.

    Args:
        url: The URL to check.
        domains_allow: Current value of `options.incoming_domains_allow()`.
        domains_deny: Current value of `options.incoming_domains_deny()`.
    """

    if domains_allow is None and domains_deny is None:
        return True
    if domains_allow and domains_deny:
        raise ValueError(
            "accept_domain_incoming: domains_allow, domains_deny are mutually exclusive parameters."
        )

    domain = get_domain(url)

    if not domain:
        log.warning(f"accept_domain_incoming received invalid URL: {url}")
        return False

    if domains_allow:
        return _domain_in_set(domain, domains_allow)

    if domains_deny:
        return not _domain_in_set(domain, domains_deny)

    return True


def accept_domain_outgoing(
    url: str,
    allow_self_mention: bool,
    domains_allow: Optional[Set[str]],
    domains_deny: Optional[Set[str]],
) -> bool:
    """Determine whether the current options allow submission of webmentions to the given URL.

    Args:
        url: The URL to check.
        allow_self_mention: Current value of `options.allow_self_mentions()`.
        domains_allow: Current value of `options.outgoing_domains_allow()`.
        domains_deny: Current value of `options.outgoing_domains_deny()`.
    """
    domain = get_domain(url)

    if not domain:
        log.warning(f"accept_domain_outgoing received invalid URL: {url}")
        return False

    if not allow_self_mention and domain == options.domain_name():
        return False
    if domains_allow and domains_deny:
        raise ValueError(
            "accept_domain_incoming: domains_allow, domains_deny are mutually exclusive parameters."
        )

    if domains_deny:
        return not _domain_in_set(domain, domains_deny)

    if domains_allow:
        return _domain_in_set(domain, domains_allow)

    return True


def _domain_in_set(domain: str, domains: Set[str]) -> bool:
    """Check if the given domain matches any of `domains`, allowing for wildcard `*.` prefix."""
    for d in domains:
        if d == domain:
            return True

        if d.startswith("*."):
            root_domain = compatibility.removeprefix(d, "*.")
            remaining_prefix = compatibility.removesuffix(domain, root_domain)
            if remaining_prefix == "" or remaining_prefix.endswith("."):
                return True

    return False
