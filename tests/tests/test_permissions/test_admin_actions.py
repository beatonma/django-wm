from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.auth.models import User
from django.test.utils import override_settings
from django.urls import path, reverse

from mentions import permissions
from mentions.models import Webmention
from tests.config.urls import core_urlpatterns
from tests.tests.util import testfunc
from tests.tests.util.testcase import WebmentionTestCase

urlpatterns = [
    *core_urlpatterns,
    path("test-admin/", admin.site.urls),
]


@override_settings(ROOT_URLCONF=__name__)
class AdminActionTests(WebmentionTestCase):
    """Tests for Webmention admin actions `approve_webmention` and `disapprove_webmention`."""

    def setUp(self) -> None:
        super().setUp()

        user_allowed = User.objects.create_user("allowed", is_staff=True)
        permissions.can_change_webmention.grant(user_allowed)

        User.objects.create_user("not_allowed", is_staff=True)

    def post_action(self, action: str, *pks):
        return self.client.post(
            reverse("admin:mentions_webmention_changelist"),
            {
                "action": action,
                ACTION_CHECKBOX_NAME: [str(pk) for pk in pks],
            },
        )


class ApprovalActionTests(AdminActionTests):
    def setUp(self) -> None:
        super().setUp()
        self.pks = [
            x.pk
            for x in [
                testfunc.create_webmention(approved=True, quote="approved"),
                testfunc.create_webmention(approved=False, quote="not approved"),
            ]
        ]

    action_approve = "mark_webmention_approved"
    action_unapprove = "mark_webmention_unapproved"

    def _assert(self, username: str, action, should_be_approved: int):
        self.client.force_login(User.objects.get(username=username))
        self.post_action(action, *self.pks)

        self.assertEqual(
            Webmention.objects.filter(approved=True).count(),
            should_be_approved,
        )

    def test_action_approve_webmention_with_permission(self):
        self._assert(
            username="allowed",
            action=self.action_approve,
            should_be_approved=2,
        )

    def test_action_approve_webmention_without_permission(self):
        self._assert(
            username="not_allowed",
            action=self.action_approve,
            should_be_approved=1,
        )

    def test_action_disapprove_webmention_with_permission(self):
        self._assert(
            username="allowed",
            action=self.action_unapprove,
            should_be_approved=0,
        )

    def test_action_disapprove_webmention_without_permission(self):
        self._assert(
            username="not_allowed",
            action=self.action_unapprove,
            should_be_approved=1,
        )


class UnreadActionTests(AdminActionTests):
    def setUp(self) -> None:
        super().setUp()
        self.pks = [
            x.pk
            for x in [
                testfunc.create_webmention(has_been_read=True, quote="read"),
                testfunc.create_webmention(has_been_read=False, quote="unread"),
            ]
        ]

    action_read = "mark_webmention_read"
    action_unread = "mark_webmention_unread"

    def _assert(self, username: str, action, should_be_approved: int):
        self.client.force_login(User.objects.get(username=username))
        self.post_action(action, *self.pks)

        self.assertEqual(
            Webmention.objects.filter(has_been_read=True).count(),
            should_be_approved,
        )

    def test_action_read_with_permission(self):
        self._assert(
            username="allowed",
            action=self.action_read,
            should_be_approved=2,
        )

    def test_action_read_without_permission(self):
        self._assert(
            username="not_allowed",
            action=self.action_read,
            should_be_approved=1,
        )

    def test_action_disapprove_with_permission(self):
        self._assert(
            username="allowed",
            action=self.action_unread,
            should_be_approved=0,
        )

    def test_action_disapprove_without_permission(self):
        self._assert(
            username="not_allowed",
            action=self.action_unread,
            should_be_approved=1,
        )
