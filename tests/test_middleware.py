from django.conf import settings
from django.urls import reverse

from tests import WebmentionTestCase
from tests.util import constants, viewname


class WebmentionHeadMiddlewareTests(WebmentionTestCase):
    """MIDDLEWARE: Tests for WebmentionHeadMiddleware"""

    def test_http_link_present_in_response(self):
        response = self.client.get(reverse(viewname.middleware))

        link = response.headers.get("Link")
        self.assertEqual(
            link,
            f'<http://{settings.DOMAIN_NAME}/{constants.namespace}/>; rel="webmention"',
        )
