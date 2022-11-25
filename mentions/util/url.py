from collections import namedtuple
from urllib.parse import urlsplit

from django.core.validators import URLValidator

__all__ = [
    "get_base_url",
    "get_domain",
    "get_urlpath",
    "get_url_validator",
]

UrlParts = namedtuple("UrlParts", ["scheme", "domain", "path", "query", "fragment"])


def get_url_validator() -> URLValidator:
    return URLValidator(schemes=["http", "https"])


def split_url(url: str) -> UrlParts:
    scheme, full_domain, path, query, fragment = urlsplit(url)
    domain = full_domain.split(":")[0]  # Remove port number if present
    return UrlParts(scheme, domain, path, query, fragment)


def get_base_url(url: str) -> str:
    scheme, domain, _, _, _ = split_url(url)
    return f"{scheme}://{domain}"


def get_domain(url: str) -> str:
    return split_url(url).domain


def get_urlpath(url: str) -> str:
    """Return the path component of the given URL."""

    return split_url(url).path
