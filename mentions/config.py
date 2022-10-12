"""Helper functions that derive from `mentions.options` values."""
from urllib.parse import urljoin

from mentions import options


def base_url() -> str:
    """Get the base URL of this server from current `options`."""
    return f"{options.url_scheme()}://{options.domain_name()}"


def build_url(path: str) -> str:
    """Construct an absolute URL for the given path on this server."""
    return urljoin(base_url(), path)
