from typing import Set

from bs4 import BeautifulSoup

__all__ = [
    "html_parser",
    "find_links_in_html",
]


def html_parser(content) -> BeautifulSoup:
    return BeautifulSoup(content, features="html5lib")


def find_links_in_html(html: str) -> Set[str]:
    """Get the raw target href of any links in the html."""
    soup = html_parser(html)
    return {a["href"] for a in soup.find_all("a", href=True)}
