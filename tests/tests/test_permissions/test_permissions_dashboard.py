from django.contrib.auth.models import User

from mentions import permissions as perms
from tests.tests.util.testcase import OptionsTestCase


class DashboardPermissionTests(OptionsTestCase):
    """Tests for mentions dashboard page."""

    def setUp(self) -> None:
        super().setUp()
        perm = perms.can_view_dashboard.get_from_db()
        user = User.objects.create_user("allowed")
        user.user_permissions.add(perm)

        User.objects.create_user("not_allowed")

    def test_dashboard_denies_anonymous(self):
        self.set_dashboard_public(False)
        response = self.get_endpoint_dashboard()

        self.assertEqual(response.status_code, 403)

    def test_dashboard_allows_anonymous_when_public(self):
        self.set_dashboard_public(True)
        response = self.get_endpoint_dashboard()

        self.assertEqual(response.status_code, 200)

    def test_dashboard_with_allowed_user(self):
        user = User.objects.get(username="allowed")
        self.assertTrue(user.has_perm(perms.can_view_dashboard.fqn()))

        self.client.force_login(user)
        response = self.get_endpoint_dashboard()

        self.assertEqual(response.status_code, 200)

    def test_dashboard_with_bad_user(self):
        user = User.objects.get(username="not_allowed")

        self.client.force_login(user)
        response = self.get_endpoint_dashboard()

        self.assertEqual(response.status_code, 403)
