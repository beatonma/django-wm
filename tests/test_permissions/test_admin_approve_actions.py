from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.auth.models import Permission, User
from django.test.utils import override_settings
from django.urls import path, reverse

from mentions.models import Webmention
from tests import WebmentionTestCase
from tests.config.test_urls import core_urlpatterns
from tests.util import testfunc

urlpatterns = [
    *core_urlpatterns,
    path("test-admin/", admin.site.urls),
]


@override_settings(ROOT_URLCONF=__name__)
class AdminApproveMentionTests(WebmentionTestCase):
    """Tests for Webmention admin actions `approve_webmention` and `disapprove_webmention`."""

    def _post_action(self, action: str, *pks):
        return self.client.post(
            reverse("admin:mentions_webmention_changelist"),
            {
                "action": action,
                ACTION_CHECKBOX_NAME: [str(pk) for pk in pks],
            },
        )

    def _post_approve(self, *pks):
        return self._post_action("approve_webmention", *pks)

    def _post_disapprove(self, *pks):
        return self._post_action("disapprove_webmention", *pks)

    def setUp(self) -> None:
        super().setUp()
        testfunc.create_webmention(approved=True, quote="approved")
        testfunc.create_webmention(approved=False, quote="not approved")

        user_allowed = User.objects.create_user("allowed", is_staff=True)
        user_allowed.user_permissions.add(
            Permission.objects.get(codename="change_webmention")
        )

        User.objects.create_user("not_allowed", is_staff=True)

    def test_action_approve_webmention_with_permission(self):
        allowed = User.objects.get(username="allowed")
        not_approved = Webmention.objects.get(quote="not approved")

        self.assertFalse(not_approved.approved)

        self.client.force_login(allowed)
        self._post_approve(not_approved.pk)

        not_approved.refresh_from_db()
        self.assertTrue(not_approved.approved)

    def test_action_approve_webmention_without_permission(self):
        not_allowed = User.objects.get(username="not_allowed")
        not_approved = Webmention.objects.get(quote="not approved")

        self.assertFalse(not_approved.approved)

        self.client.force_login(not_allowed)
        self._post_approve(not_approved.pk)

        not_approved.refresh_from_db()
        self.assertFalse(not_approved.approved)

    def test_action_disapprove_webmention_with_permission(self):
        allowed = User.objects.get(username="allowed")
        approved = Webmention.objects.get(quote="approved")

        self.assertTrue(approved.approved)

        self.client.force_login(allowed)
        self._post_disapprove(approved.pk)

        approved.refresh_from_db()
        self.assertFalse(approved.approved)

    def test_action_disapprove_webmention_without_permission(self):
        not_allowed = User.objects.get(username="not_allowed")
        approved = Webmention.objects.get(quote="approved")

        self.assertTrue(approved.approved)

        self.client.force_login(not_allowed)
        self._post_disapprove(approved.pk)

        approved.refresh_from_db()
        self.assertTrue(approved.approved)
