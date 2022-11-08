from tests.tests.util import testfunc
from tests.tests.util.testcase import WebmentionTestCase


class MentionsEndpointsTests(WebmentionTestCase):
    """ENDPOINT: Make sure endpoints are accessible."""

    def test_incoming_endpoint(self):
        """Primary endpoint is accessible."""
        response = self.client.get(testfunc.endpoint_submit_webmention())
        self.assertEqual(200, response.status_code)

    def test_get_endpoint(self):
        """`/get` endpoint is accessible."""
        obj = testfunc.create_mentionable_object()

        response = self.client.get(
            testfunc.endpoint_get_webmentions(), data={"url": obj.get_absolute_url()}
        )
        self.assertEqual(200, response.status_code)

    def test_get_by_type_endpoint(self):
        """`/get-by-type` endpoint is accessible."""
        obj = testfunc.create_mentionable_object()

        response = self.client.get(
            testfunc.endpoint_get_webmentions_by_type(),
            data={"url": obj.get_absolute_url()},
        )
        self.assertEqual(200, response.status_code)
