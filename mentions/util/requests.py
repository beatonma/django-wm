import requests
from requests import Response

from mentions import options

__all__ = [
    "http_get",
    "http_post",
]

HTTP_TIMEOUT_SECONDS = options.timeout()

HTTP_HEADERS = {
    "User-Agent": options.user_agent(),
}


def http_get(url: str) -> Response:
    return requests.get(
        url,
        headers=HTTP_HEADERS,
        timeout=HTTP_TIMEOUT_SECONDS,
    )


def http_post(url: str, data: dict) -> Response:
    return requests.post(
        url,
        data=data,
        headers=HTTP_HEADERS,
        timeout=HTTP_TIMEOUT_SECONDS,
    )
