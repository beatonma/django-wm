from django.contrib.auth.models import User
from django.test.utils import override_settings
from django.urls import reverse

from mentions import contract, permissions
from tests.tests.test_templates.views import TEMPLATE_TEST_VIEW_NAME
from tests.tests.util import testfunc
from tests.tests.util.testcase import WebmentionTestCase


@override_settings(ROOT_URLCONF="tests.tests.test_templates.views")
class ContextProcessorTests(WebmentionTestCase):
    def setUp(self) -> None:
        testfunc.create_webmention(has_been_read=False)

        self.user = User.objects.create_user("allowed-user")
        permissions.can_change_webmention.grant(self.user)

    def test_unread_webmentions_with_permission(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse(TEMPLATE_TEST_VIEW_NAME))

        unread = response.context.get(contract.CONTEXT_UNREAD_WEBMENTIONS)
        self.assertEqual(unread.count(), 1)

    def test_unread_webmentions_without_permission(self):
        response = self.client.get(reverse(TEMPLATE_TEST_VIEW_NAME))

        unread = response.context.get(contract.CONTEXT_UNREAD_WEBMENTIONS)
        self.assertIsNone(unread)
