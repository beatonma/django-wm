from django.http import HttpResponse
from django.test.utils import override_settings
from django.urls import path, reverse
from django.views import View

from mentions import config
from tests.config.urls import core_urlpatterns
from tests.tests.util import constants, snippets
from tests.tests.util.testcase import WebmentionTestCase

VIEW_NAME = "middleware"


class MiddlewareView(View):
    """Empty view, just for testing WebmentionHeadMiddleware."""

    def get(self, request):
        headers = {}
        if request.GET.get("additional_links"):
            headers["Link"] = snippets.http_header_link(
                "https://websub.io",
                rel="websub",
            )

        return HttpResponse(status=200, headers=headers)


urlpatterns = core_urlpatterns + [
    path(
        "middleware/",
        MiddlewareView.as_view(),
        name=VIEW_NAME,
    ),
]


@override_settings(ROOT_URLCONF=__name__)
class WebmentionHeadMiddlewareTests(WebmentionTestCase):
    """MIDDLEWARE: Tests for WebmentionHeadMiddleware"""

    def setUp(self) -> None:
        super().setUp()
        self.endpoint_http_link = (
            f'<{config.build_url(f"/{constants.namespace}/")}>; rel="webmention"'
        )

    def test_middleware_adds_endpoint_to_http_headers(self):
        response = self.client.get(reverse(VIEW_NAME))

        link = response.headers.get("Link")
        self.assertEqual(link, self.endpoint_http_link)

    def test_middleware_keeps_existing_links_in_http_headers(self):
        """Ensure that middleware does not remove any existing Links from headers."""
        response = self.client.get(f"{reverse(VIEW_NAME)}?additional_links=1")

        links = response.headers.get("Link")
        self.assertIn(
            self.endpoint_http_link,
            links,
        )

        self.assertIn('<https://websub.io>; rel="websub"', links)

        self.assertEqual(
            f'<https://websub.io>; rel="websub",{self.endpoint_http_link}', links
        )
