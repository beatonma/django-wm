import requests
from requests import Response

from mentions import options

__all__ = [
    "http_get",
    "http_post",
]

HTTP_TIMEOUT_SECONDS = options.timeout()


def http_get(url: str) -> Response:
    return requests.get(url, timeout=HTTP_TIMEOUT_SECONDS)


def http_post(url: str, data: dict) -> Response:
    return requests.post(url, data=data, timeout=HTTP_TIMEOUT_SECONDS)
