from unittest.mock import patch

from tests.tests.util import testfunc
from tests.tests.util.testcase import WebmentionTestCase


class PrimaryEndpointTests(WebmentionTestCase):
    """ENDPOINT `/`"""

    def setUp(self) -> None:
        self.target_url = testfunc.get_absolute_url_for_object(
            testfunc.create_mentionable_object()
        )

    def _mock_post(self, data: dict, accept: bool) -> int:
        with patch("mentions.views.submit.handle_incoming_webmention") as mock_func:
            response = self.client.post(
                testfunc.endpoint_submit_webmention_absolute(),
                data=data,
            )
            self.assertEqual(accept, mock_func.called)
            return response.status_code

    def test_primary_endpoint_accepts_webmentions(self):
        """Valid POST request accepts webmention for processing and returns successful HTTP code 202."""

        data = {
            "source": testfunc.random_url(),
            "target": self.target_url,
        }

        response_code = self._mock_post(data, accept=True)

        self.assertEqual(202, response_code)

    def test_primary_endpoint_rejects_missing_target(self):
        """Missing `target` parameter rejects webmention and returns HTTP 400."""
        data = {"source": testfunc.random_url()}
        response_code = self._mock_post(data, accept=False)

        self.assertEqual(400, response_code)

    def test_primary_endpoint_rejects_missing_source(self):
        """Missing `source` parameter rejects webmention and returns HTTP 400."""
        data = {"target": testfunc.random_url()}
        response_code = self._mock_post(data, accept=False)

        self.assertEqual(400, response_code)

    def test_primary_endpoint_rejects_invalid_target(self):
        """Invalid `target` rejects webmention and returns 400."""
        data = {
            "source": testfunc.random_url(),
            "target": "htt://bad-url.or",
        }

        response_code = self._mock_post(data, accept=False)
        self.assertEqual(400, response_code)

    def test_primary_endpoint_rejects_invalid_source(self):
        """Invalid `source` rejects webmention and returns 400."""
        data = {
            "source": "https://bad//url",
            "target": self.target_url,
        }

        response_code = self._mock_post(data, accept=False)
        self.assertEqual(400, response_code)

    def test_primary_endpoint_get(self):
        response = self.get_endpoint_primary()

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "mentions/webmention-submit-manual.html")
