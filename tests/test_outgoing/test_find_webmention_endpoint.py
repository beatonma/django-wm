from requests.structures import CaseInsensitiveDict

from mentions.tasks.outgoing.parsing.webmention_endpoint import (
    get_endpoint_in_http_headers,
)
from tests import WebmentionTestCase
from tests.util import snippets, testfunc


class FindWebmentionEndpointTests(WebmentionTestCase):
    def test_find_endpoint_in_http_headers(self):
        headers = CaseInsensitiveDict(
            {
                "Link": snippets.http_link_endpoint(),
            }
        )

        self.assertEqual(
            testfunc.endpoint_submit_webmention(),
            get_endpoint_in_http_headers(headers),
        )

    def test_find_endpoint_in_http_headers_with_many_links(self):
        headers = CaseInsensitiveDict(
            {
                "Link": ", ".join(
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
                ),
            }
        )

        self.assertEqual(
            "https://webmention.io",
            get_endpoint_in_http_headers(headers),
        )
