from django.urls import reverse

from mentions import config
from tests import WebmentionTestCase
from tests.util import constants, viewname


class WebmentionHeadMiddlewareTests(WebmentionTestCase):
    """MIDDLEWARE: Tests for WebmentionHeadMiddleware"""

    def setUp(self) -> None:
        super().setUp()
        self.endpoint_http_link = (
            f'<{config.build_url(f"/{constants.namespace}/")}>; rel="webmention"'
        )

    def test_middleware_adds_endpoint_to_http_headers(self):
        response = self.client.get(reverse(viewname.middleware))

        link = response.headers.get("Link")
        self.assertEqual(link, self.endpoint_http_link)

    def test_middleware_keeps_existing_links_in_http_headers(self):
        """Ensure that middleware does not remove any existing Links from headers."""
        response = self.client.get(f"{reverse(viewname.middleware)}?additional_links=1")

        links = response.headers.get("Link")
        self.assertIn(
            self.endpoint_http_link,
            links,
        )

        self.assertIn('<https://websub.io>; rel="websub"', links)

        self.assertEqual(
            f'<https://websub.io>; rel="websub",{self.endpoint_http_link}', links
        )
