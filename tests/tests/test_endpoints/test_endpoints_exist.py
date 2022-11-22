from django.urls import reverse

from mentions.views import view_names
from tests.tests.util import testfunc
from tests.tests.util.testcase import OptionsTestCase


class MentionsEndpointsTests(OptionsTestCase):
    """ENDPOINT: Make sure endpoints are accessible."""

    def test_incoming_endpoint(self):
        """Primary endpoint is accessible and uses template."""
        response = self.client.get(testfunc.endpoint_submit_webmention())
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "mentions/webmention-submit-manual.html")

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

    def test_dashboard(self):
        """/dashboard is accessible and uses template."""
        self.set_dashboard_public(True)
        response = self.client.get(reverse(view_names.webmention_dashboard))

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "mentions/webmention-dashboard.html")
