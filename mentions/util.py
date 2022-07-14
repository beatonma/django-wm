import logging
from typing import Tuple
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

log = logging.getLogger(__name__)


def split_url(target_url: str) -> Tuple[str, str, str]:
    scheme, full_domain, path, _, _ = urlsplit(target_url)
    domain = full_domain.split(":")[0]  # Remove port number if present
    return scheme, domain, path


def html_parser(content) -> BeautifulSoup:
    return BeautifulSoup(content, features="html5lib")
