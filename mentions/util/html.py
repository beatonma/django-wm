import re
from typing import List

from bs4 import BeautifulSoup, ResultSet, Tag

__all__ = [
    "html_parser",
    "find_links_in_html",
    "find_links_in_soup",
]


def html_parser(content: str) -> Tag:
    soup = BeautifulSoup(content, features="html5lib")

    return _clean_soup(soup)


def find_links_in_html(html: str) -> List[Tag]:
    soup = html_parser(html)
    return find_links_in_soup(soup)


def find_links_in_soup(soup: Tag) -> ResultSet:
    return soup.find_all("a", href=True)


def _clean_soup(soup: Tag) -> Tag:
    """Remove any CSS classes that may look like `h-` microformat containers
    (e.g. `tailwindcss` height utilities) as these interfere with microformat parsing.
    """

    pattern = re.compile(r"(h-(?!adr|card|entry|feed|geo|cite|event).+)")
    for tag in soup.find_all(class_=True):
        classes = tag.get("class")
        filtered_classes = [c for c in classes if not pattern.match(c)]
        if filtered_classes:
            tag["class"] = filtered_classes
        else:
            del tag["class"]

    return soup
