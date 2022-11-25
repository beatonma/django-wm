from django.contrib.auth.models import User
from django.test.utils import override_settings
from django.urls import path, reverse
from django.views.generic import TemplateView

from mentions import permissions
from mentions.tasks.outgoing import remote
from mentions.views import view_names
from tests.config.urls import core_urlpatterns
from tests.tests.util.testcase import OptionsTestCase

VIEW_NAME = "test-template-tags-view"


class TemplateTagTestView(TemplateView):
    """Render page to test `{% webmentions_endpoint %}` tag."""

    template_name = "templatetags_example.html"


urlpatterns = core_urlpatterns + [
    path(
        "templatetagstest/",
        TemplateTagTestView.as_view(),
        name=VIEW_NAME,
    ),
]


@override_settings(ROOT_URLCONF=__name__)
class TemplateTagTests(OptionsTestCase):
    """TEMPLATE: Test template tags."""

    def setUp(self) -> None:
        super().setUp()
        self.test_view_url = reverse(VIEW_NAME)
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
