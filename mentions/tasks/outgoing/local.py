from typing import Set

from mentions.util import html_parser


def get_target_links_in_text(text: str) -> Set[str]:
    """Get any links from the text that should be treated as webmention targets."""
    links = _find_links_in_text(text)

    # Filter self-linking #anchors.
    links = {link for link in links if not link.startswith("#")}

    return links


def _find_links_in_text(text: str) -> Set[str]:
    """Get the raw target href of any links in the text."""
    soup = html_parser(text)
    return {a["href"] for a in soup.find_all("a", href=True)}
