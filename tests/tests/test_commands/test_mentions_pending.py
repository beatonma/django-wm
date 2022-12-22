from unittest.mock import patch

from django.core.management import call_command

from tests.tests.util.testcase import WebmentionTestCase


class MentionsPendingTests(WebmentionTestCase):
    def test_mentions_pending_calls_task(self):
        with patch("mentions.tasks.scheduling.handle_pending_webmentions") as task:
            call_command("mentions_pending")
            self.assertTrue(task.called)


class DeprecatedMentionsPendingTests(WebmentionTestCase):
    def test_deprecated_pending_mentions_still_works(self):
        with patch(
            "mentions.management.commands.mentions_pending.handle_pending_webmentions"
        ) as task:
            call_command("pending_mentions")
            self.assertTrue(task.called)
