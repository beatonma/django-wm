import requests

from mentions.exceptions import SourceDoesNotLink, SourceNotAccessible
from mentions.models import HCard, Webmention
from mentions.tasks.incoming.parsing.hcard import parse_hcard
from mentions.tasks.incoming.parsing.post_type import parse_post_type
from mentions.util import html_parser


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
        response = requests.get(source_url)
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


def update_metadata_from_source(
    wm: Webmention,
    html: str,
    target_url: str,
) -> Webmention:

    """Update the webmention with metadata from its context in the source html.

    Adds HCard and webmention type, if available.

    Raises:
        SourceDoesNotLink: If the `target_url` does not appear in the given text.
    """

    soup = html_parser(html)
    link = soup.find("a", href=target_url)

    if link is None:
        raise SourceDoesNotLink()

    post_type = parse_post_type(link)
    wm.post_type = post_type.name.lower() if post_type else None
    wm.hcard = parse_hcard(soup)
    return wm
