import logging
from typing import Callable, Optional
from unittest.mock import Mock, patch

import requests
from requests.structures import CaseInsensitiveDict

log = logging.getLogger(__name__)


class MockResponse:
    """Mock of requests.Response."""

    url: str
    headers: Optional[CaseInsensitiveDict]
    text: Optional[str]
    status_code: Optional[int]

    def __init__(
        self,
        url: str,
        headers: Optional[dict] = None,
        text: Optional[str] = None,
        status_code: Optional[int] = None,
    ):
        self.url = url
        self.text = text
        self.status_code = status_code
        self.headers = CaseInsensitiveDict(headers or {"Content-Type": "text/html"})
        log.debug(self)

    def __str__(self):
        return f"[{self.status_code}] {self.url}"


def patch_http_get(
    status_code: int = 200,
    text: Optional[str] = None,
    headers: Optional[dict] = None,
    response: Optional[Callable] = None,
):
    headers = headers or {"content-type": "text/html"}

    side_effect = (
        response
        if response
        else lambda url, **kw: MockResponse(
            url,
            headers=headers,
            text=text or "",
            status_code=status_code,
        )
    )

    return patch.object(
        requests,
        "get",
        Mock(side_effect=side_effect),
    )


def patch_http_post(
    status_code: int = 200,
    headers: Optional[dict] = None,
    response: Optional[Callable] = None,
):
    side_effect = (
        response
        if response
        else lambda url, **kw: MockResponse(
            url,
            headers=headers,
            status_code=status_code,
        )
    )

    return patch.object(
        requests,
        "post",
        Mock(side_effect=side_effect),
    )
