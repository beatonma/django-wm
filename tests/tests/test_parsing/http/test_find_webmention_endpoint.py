from typing import List, Union

from requests.structures import CaseInsensitiveDict

from mentions.tasks.outgoing.parsing.webmention_endpoint import (
    get_endpoint_in_http_headers,
)
from tests.tests.util import snippets, testfunc
from tests.tests.util.testcase import WebmentionTestCase


def _build_headers(link: Union[List[str], str]) -> CaseInsensitiveDict:
    if isinstance(link, str):
        return CaseInsensitiveDict(
            {
                "Link": link,
            }
        )

    return CaseInsensitiveDict(
        {
            "Link": ", ".join(link),
        }
    )


class FindWebmentionEndpointHttpHeadersTests(WebmentionTestCase):
    def test_find_endpoint_in_http_headers(self):
        headers = _build_headers(snippets.http_link_endpoint())

        self.assertEqual(
            testfunc.endpoint_submit_webmention(),
            get_endpoint_in_http_headers(headers),
        )

    def test_find_endpoint_in_http_headers_with_additional_attrs(self):
        headers = _build_headers(
            snippets.http_header_link(
                "https://endpoint.org",
                title="Title",
                rel="webmention",
                hreflang="en-GB",
            )
        )

        self.assertEqual("https://endpoint.org", get_endpoint_in_http_headers(headers))

    def test_find_endpoint_in_http_headers_with_many_links(self):
        headers = _build_headers(
            [
                snippets.http_header_link(
                    testfunc.random_url(),
                    **{
                        "rel": "preload",
                        "as": "script",
                        "nopush": None,
                    },
                ),
                snippets.http_header_link(
                    "https://websub.io",
                    rel="websub",
                ),
                snippets.http_header_link(
                    testfunc.random_url(),
                    **{
                        "rel": "preload",
                        "as": "script",
                        "nopush": None,
                    },
                ),
                snippets.http_header_link(
                    "https://webmention.io",
                    rel="webmention",
                ),
                snippets.http_header_link(
                    testfunc.random_url(),
                    **{
                        "rel": "preload",
                        "as": "script",
                        "nopush": None,
                    },
                ),
            ]
        )

        self.assertEqual(
            "https://webmention.io",
            get_endpoint_in_http_headers(headers),
        )
