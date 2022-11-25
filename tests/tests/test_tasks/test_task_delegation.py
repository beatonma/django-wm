from unittest.mock import patch

from mentions.models import PendingIncomingWebmention, PendingOutgoingContent
from mentions.tasks.scheduling import (
    _maybe_reschedule_handle_pending_webmentions, _task_handle_incoming,
    _task_handle_outgoing, handle_incoming_webmention,
    handle_outgoing_webmentions, handle_pending_webmentions)
from tests.tests.util import testfunc
from tests.tests.util.testcase import OptionsTestCase, WebmentionTestCase


class IncomingWebmentionDelegationTests(OptionsTestCase):
    """INCOMING: Check behaviour of scheduling.handle_incoming_webmention based on settings.WEBMENTIONS_USE_CELERY."""

    def setUp(self) -> None:
        super().setUp()

        obj = testfunc.create_mentionable_object()
        self.source = testfunc.random_url()
        self.target = testfunc.get_absolute_url_for_object(obj)
        self.sent_by = "localhost"

    def test_incoming_with_celery_disabled(self):
        """handle_incoming_webmention creates PendingIncomingWebmention when celery is disabled."""
        self.enable_celery(False)

        handle_incoming_webmention(self.source, self.target, self.sent_by)

        pending = self.assert_exists(PendingIncomingWebmention)
        self.assertEqual(pending.source_url, self.source)
        self.assertEqual(pending.target_url, self.target)
        self.assertEqual(pending.sent_by, self.sent_by)

    def test_incoming_with_celery_enabled(self):
        """handle_incoming_webmention delegates to celery when it is enabled."""
        self.enable_celery(True)

        with patch(
            "mentions.tasks.scheduling._task_handle_incoming.delay"
        ) as handle_task:
            handle_incoming_webmention(self.source, self.target, self.sent_by)
            self.assertTrue(handle_task.called)

        self.assert_not_exists(PendingIncomingWebmention)

    def test_task_calls_process_and_reschedule(self):
        self.enable_celery(True)

        with patch(
            "mentions.tasks.scheduling.process_incoming_webmention"
        ) as process, patch(
            "mentions.tasks.scheduling._maybe_reschedule_handle_pending_webmentions"
        ) as reschedule:
            _task_handle_incoming(self.source, self.target, self.sent_by)
            self.assertTrue(process.called)
            self.assertTrue(reschedule.called)


class OutgoingWebmentionDelegationTests(OptionsTestCase):
    """OUTGOING: Check behaviour of scheduling.handle_outgoing_webmentions based on settings.WEBMENTIONS_USE_CELERY."""

    def setUp(self) -> None:
        super().setUp()

        obj = testfunc.create_mentionable_object("Content that might mention a URL")
        self.absolute_url = obj.get_absolute_url()
        self.all_text = obj.get_content_html()

    def test_outgoing_with_celery_disabled(self):
        """handle_outgoing_webmentions creates PendingOutgoingContent when celery is disabled."""
        self.enable_celery(False)

        handle_outgoing_webmentions(self.absolute_url, self.all_text)

        pending = self.assert_exists(PendingOutgoingContent)
        self.assertEqual(pending.absolute_url, self.absolute_url)
        self.assertEqual(pending.text, self.all_text)

    def test_outgoing_with_celery_enabled(self):
        """handle_outgoing_webmentions delegates to celery when it is enabled."""
        self.enable_celery(True)

        with patch(
            "mentions.tasks.scheduling._task_handle_outgoing.delay"
        ) as handle_task:
            handle_outgoing_webmentions(self.absolute_url, self.all_text)
            self.assertTrue(handle_task.called)

        self.assert_not_exists(PendingOutgoingContent)

    def test_task_calls_process_and_reschedule(self):
        self.enable_celery(True)

        with patch(
            "mentions.tasks.scheduling.process_outgoing_webmentions"
        ) as process, patch(
            "mentions.tasks.scheduling._maybe_reschedule_handle_pending_webmentions"
        ) as reschedule:
            _task_handle_outgoing(self.absolute_url, self.all_text)
            self.assertTrue(process.called)
            self.assertTrue(reschedule.called)


class HandlePendingMentionsTests(WebmentionTestCase):
    """PENDING: Check behaviour of scheduling.handle_pending_webmentions."""

    def setUp(self) -> None:
        super().setUp()

        source = testfunc.random_url()
        obj = testfunc.create_mentionable_object(content=testfunc.random_str())

        PendingIncomingWebmention.objects.create(
            source_url=source,
            target_url=testfunc.get_absolute_url_for_object(obj),
            sent_by="localhost",
        )
        PendingOutgoingContent.objects.create(
            absolute_url=obj.get_absolute_url(),
            text=obj.content,
        )

    def test_handle_pending_incoming_mentions(self):
        """PendingIncomingWebmentions are passed to process_incoming_webmention."""
        with patch(
            "mentions.tasks.scheduling.process_incoming_webmention"
        ) as incoming_task, patch(
            "mentions.tasks.scheduling.process_outgoing_webmentions"
        ) as outgoing_task, patch(
            "mentions.tasks.scheduling._reschedule_handle_pending_webmentions"
        ):
            handle_pending_webmentions(incoming=True, outgoing=False)
            self.assertTrue(incoming_task.called)
            self.assertFalse(outgoing_task.called)

    def test_handle_pending_outgoing_content(self):
        """PendingOutgoingContent are passed to process_outgoing_webmentions."""
        with patch(
            "mentions.tasks.scheduling.process_outgoing_webmentions"
        ) as outgoing_task, patch(
            "mentions.tasks.scheduling.process_incoming_webmention"
        ) as incoming_task, patch(
            "mentions.tasks.scheduling._reschedule_handle_pending_webmentions"
        ):
            handle_pending_webmentions(incoming=False, outgoing=True)
            self.assertTrue(outgoing_task.called)
            self.assertFalse(incoming_task.called)

    def test_celery_rescheduled_if_pending(self):
        with patch(
            "mentions.tasks.scheduling._reschedule_handle_pending_webmentions"
        ) as reschedule:
            _maybe_reschedule_handle_pending_webmentions()
            self.assertTrue(reschedule.called)

    def test_celery_not_rescheduled_if_nothing_pending_retry(self):
        with patch(
            "mentions.tasks.scheduling._reschedule_handle_pending_webmentions"
        ) as reschedule:
            PendingIncomingWebmention.objects.all().update(is_awaiting_retry=False)

            _maybe_reschedule_handle_pending_webmentions()
            self.assertFalse(reschedule.called)
