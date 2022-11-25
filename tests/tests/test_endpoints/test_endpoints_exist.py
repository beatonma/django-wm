from tests.tests.util import testfunc
from tests.tests.util.testcase import OptionsTestCase


class MentionsEndpointsTests(OptionsTestCase):
    """ENDPOINT: Make sure endpoints are accessible."""

    def test_incoming_endpoint(self):
        """Primary endpoint is accessible and uses template."""
        response = self.get_endpoint_primary()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "mentions/webmention-submit-manual.html")

    def test_get_endpoint(self):
        """`/get` endpoint is accessible."""
        obj = testfunc.create_mentionable_object()
        response = self.get_endpoint_mentions(url=obj.get_absolute_url())

        self.assertEqual(200, response.status_code)

    def test_get_by_type_endpoint(self):
        """`/get-by-type` endpoint is accessible."""
        obj = testfunc.create_mentionable_object()
        response = self.get_endpoint_mentions_by_type(url=obj.get_absolute_url())

        self.assertEqual(200, response.status_code)

    def test_dashboard(self):
        """/dashboard is accessible and uses template."""
        self.set_dashboard_public(True)
        response = self.get_endpoint_dashboard()

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "mentions/webmention-dashboard.html")
