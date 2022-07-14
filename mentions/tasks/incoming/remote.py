from typing import Optional

import requests
from bs4 import Tag

from mentions.exceptions import SourceDoesNotLink, SourceNotAccessible
from mentions.models import HCard, Webmention
from mentions.models.mixins.quotable import IncomingMentionType
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

    post_type = parse_link_type(link)
    wm.post_type = post_type.name.lower() if post_type else None
    wm.hcard = HCard.from_soup(soup, save=True)
    return wm


def parse_link_type(link: Tag) -> Optional[IncomingMentionType]:
    """Return any available type information in the context of the link.

    This may be available as a class on the link itself, or on a parent element
    that is marked with h-cite."""

    def find_mention_type_in_classlist(element: Tag) -> Optional[IncomingMentionType]:
        if element.has_attr("class"):
            classes = set(element["class"])

            for _type in IncomingMentionType.__members__.values():
                if _type.value in classes:
                    return _type

    link_type = find_mention_type_in_classlist(link)
    if link_type is not None:
        return link_type

    hcite = link.find_parent(class_="h-cite")
    if hcite:
        return find_mention_type_in_classlist(hcite)
