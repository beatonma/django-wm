from typing import Tuple
from urllib.parse import urlsplit

from django.core.validators import URLValidator

__all__ = [
    "get_base_url",
    "get_url_validator",
    "split_url",
]


def get_url_validator() -> URLValidator:
    return URLValidator(schemes=["http", "https"])


def split_url(url: str) -> Tuple[str, str, str]:
    scheme, full_domain, path, _, _ = urlsplit(url)
    domain = full_domain.split(":")[0]  # Remove port number if present
    return scheme, domain, path


def get_base_url(url: str) -> str:
    scheme, domain, _ = split_url(url)
    return f"{scheme://{domain}}"
