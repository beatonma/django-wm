import logging
from typing import Tuple
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup
from requests import Response

from mentions import options

log = logging.getLogger(__name__)


HTTP_TIMEOUT_SECONDS = options.timeout()


def split_url(target_url: str) -> Tuple[str, str, str]:
    scheme, full_domain, path, _, _ = urlsplit(target_url)
    domain = full_domain.split(":")[0]  # Remove port number if present
    return scheme, domain, path


def html_parser(content) -> BeautifulSoup:
    return BeautifulSoup(content, features="html5lib")


def http_get(url: str) -> Response:
    return requests.get(url, timeout=HTTP_TIMEOUT_SECONDS)


def http_post(url: str, data: dict) -> Response:
    return requests.post(url, data=data, timeout=HTTP_TIMEOUT_SECONDS)
