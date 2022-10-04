from typing import Set

from mentions.util import html_parser

__all__ = [
    "get_target_links_in_text",
    "is_valid_target",
]


def get_target_links_in_text(text: str) -> Set[str]:
    """Get any links from the text that should be treated as webmention targets."""
    links = _find_links_in_text(text)
    links = {link for link in links if is_valid_target(link)}

    return links


def is_valid_target(url: str) -> bool:
    if url.startswith("#"):
        return False

    return True


def _find_links_in_text(text: str) -> Set[str]:
    """Get the raw target href of any links in the text."""
    soup = html_parser(text)
    return {a["href"] for a in soup.find_all("a", href=True)}
