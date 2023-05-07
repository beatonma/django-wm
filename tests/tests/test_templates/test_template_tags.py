from django.contrib.auth.models import User
from django.test.utils import override_settings
from django.urls import reverse

from mentions import permissions
from mentions.tasks.outgoing import remote
from mentions.views import view_names
from tests.tests.test_templates.views import TEMPLATE_TEST_VIEW_NAME
from tests.tests.util.testcase import OptionsTestCase


@override_settings(ROOT_URLCONF="tests.tests.test_templates.views")
class TemplateTagTests(OptionsTestCase):
    """TEMPLATE: Test template tags."""

    def setUp(self) -> None:
        super().setUp()
        self.test_view_url = reverse(TEMPLATE_TEST_VIEW_NAME)
        self.user = User.objects.create_user("dashboard-user")
        permissions.can_view_dashboard.grant(self.user)

    def test_webmentions_endpoint_renders_correctly(self):
        """{% webmentions_endpoint %} renders correctly."""
        expected_endpoint = reverse(view_names.webmention_api_incoming)
        response = self.client.get(self.test_view_url)

        self.assertContains(response, expected_endpoint)

        self.assertEqual(
            remote.get_endpoint_in_html(response.content),
            expected_endpoint,
        )

    def test_webmentions_dashbaord_without_permission_is_empty(self):
        """{% webmentions_dashboard %} renders correctly."""
        self.set_dashboard_public(False)
        expected_endpoint = reverse(view_names.webmention_dashboard)
        response = self.client.get(self.test_view_url)

        self.assertNotContains(response, expected_endpoint)

    def test_webmentions_dashboard_with_permission_renders_correctly(self):
        self.set_dashboard_public(False)
        expected_endpoint = reverse(view_names.webmention_dashboard)
        self.client.force_login(self.user)
        response = self.client.get(self.test_view_url)

        self.assertContains(response, expected_endpoint, count=2)
        self.assertContains(response, "Webmentions Dashboard")
        self.assertContains(response, "Custom dashboard title")

    def test_webmentions_dashboard_with_public_dashboard_renders_correctly(self):
        self.set_dashboard_public(True)
        expected_endpoint = reverse(view_names.webmention_dashboard)
        response = self.client.get(self.test_view_url)

        self.assertContains(response, expected_endpoint)
