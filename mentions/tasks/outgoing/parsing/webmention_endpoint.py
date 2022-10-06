import logging
import re
from typing import Optional

from bs4 import BeautifulSoup
from requests.structures import CaseInsensitiveDict

from mentions.util import html_parser

__all__ = [
    "get_endpoint_in_html",
    "get_endpoint_in_html_body",
    "get_endpoint_in_html_head",
    "get_endpoint_in_http_headers",
]

HTTP_LINK_PATTERN = re.compile(
    r"<(?P<url>[^>]+?)>;([^,]*;)*\s*rel=(?P<quote>['\"]?)webmention(?P=quote)"
)

log = logging.getLogger(__name__)


def get_endpoint_in_http_headers(headers: CaseInsensitiveDict) -> Optional[str]:
    link = headers.get("Link")
    if link is None:
        return

    if "webmention" in link:
        match = re.search(HTTP_LINK_PATTERN, link)
        if match is None:
            return

        endpoint = match.group("url")
        log.debug(f"Webmention endpoint found in HTTP header: '{endpoint}'")
        return endpoint


def get_endpoint_in_html(html: str) -> Optional[str]:
    """Search for a webmention endpoint in HTML."""
    soup = html_parser(html)

    return get_endpoint_in_html_head(soup) or get_endpoint_in_html_body(soup)


def get_endpoint_in_html_head(soup: BeautifulSoup) -> Optional[str]:
    """Check HTML <head> for <link> webmention endpoint."""
    links = soup.head.find_all("link", href=True, rel=True)
    for link in links:
        if "webmention" in link["rel"]:
            endpoint = link["href"]
            log.debug(f"Webmention endpoint found in document head: {endpoint}")
            return endpoint


def get_endpoint_in_html_body(soup: BeautifulSoup) -> Optional[str]:
    """Check HTML <body> for <a> webmention endpoint."""
    links = soup.body.find_all("a", href=True, rel=True)
    for link in links:
        if "webmention" in link["rel"]:
            endpoint = link["href"]
            log.debug(f"Webmention endpoint found in document body: {endpoint}")
            return endpoint
