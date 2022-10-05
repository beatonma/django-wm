from tests import MetaTestCase
from tests.util import snippets


class SnippetsTestCase(MetaTestCase):
    def test_http_header_link(self):

        self.assertEqual(
            """<https://beatonma.org/webmentions/>; rel="webmentions\"""",
            snippets.http_header_link(
                "https://beatonma.org/webmentions/",
                rel="webmentions",
            ),
        )

        self.assertEqual(
            """<https://beatonma.org/script.js>; rel="preload"; as="script"; nopush""",
            snippets.http_header_link(
                "https://beatonma.org/script.js",
                **{
                    "rel": "preload",
                    "as": "script",
                    "nopush": None,
                },
            ),
        )
