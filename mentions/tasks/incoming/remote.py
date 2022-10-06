from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin

from mentions.exceptions import SourceDoesNotLink, SourceNotAccessible
from mentions.models import HCard
from mentions.models.mixins import IncomingMentionType
from mentions.tasks.incoming.parsing import (
    find_related_hcard,
    parse_hcard,
    parse_post_type,
)
from mentions.util import html_parser, http_get

__all__ = [
    "get_source_html",
    "get_metadata_from_source",
]

from mentions.util.html import find_links_in_soup


def get_source_html(source_url: str) -> str:
    """Confirm source exists as HTML and return its content.

    Verify that the source URL returns an HTML page with a successful
    status code.

    Args:
        source_url: The URL that mentions our content.

    Raises:
        SourceNotAccessible: If the `source_url` cannot be resolved, returns an error code, or
                             is an unexpected content type.
    """

    try:
        response = http_get(source_url)
    except Exception as e:
        raise SourceNotAccessible(f"Requests error: {e}")

    if response.status_code >= 300:
        raise SourceNotAccessible(
            f"Source '{source_url}' returned error code [{response.status_code}]"
        )

    content_type = response.headers["content-type"]  # Case-insensitive
    if "text/html" not in content_type:
        raise SourceNotAccessible(
            f"Source '{source_url}' returned unexpected content type: {content_type}"
        )

    return response.text


@dataclass
class WebmentionMetadata:
    post_type: Optional[IncomingMentionType]
    hcard: Optional[HCard]


def get_metadata_from_source(
    html: str,
    target_url: str,
    source_url: str,
) -> WebmentionMetadata:
    """Retrieve contextual data about the mention from the html source.

    Raises:
        SourceDoesNotLink: If the `target_url` is not linked in the given html.
    """

    soup = html_parser(html)
    links = find_links_in_soup(soup)

    for link in links:
        absolute_url = urljoin(source_url, link["href"])
        if absolute_url == target_url:
            break
    else:
        raise SourceDoesNotLink()

    post_type = parse_post_type(link)

    hcard = find_related_hcard(link)
    if not hcard:
        hcard = parse_hcard(soup, recursive=False)

    return WebmentionMetadata(
        post_type=post_type.name.lower() if post_type else None,
        hcard=hcard,
    )
