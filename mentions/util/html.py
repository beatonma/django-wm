from typing import List, Set

from bs4 import BeautifulSoup, ResultSet, Tag

__all__ = [
    "html_parser",
    "find_links_in_html",
    "find_links_in_soup",
]


def html_parser(content) -> BeautifulSoup:
    return BeautifulSoup(content, features="html5lib")


def find_links_in_html(html: str) -> List[Tag]:
    soup = html_parser(html)
    return find_links_in_soup(soup)


def find_links_in_soup(soup: BeautifulSoup) -> ResultSet:
    return soup.find_all("a", href=True)
