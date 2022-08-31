from unittest.mock import patch

from django.http import QueryDict

from mentions.models import PendingIncomingWebmention, PendingOutgoingContent
from mentions.tasks.scheduling import (
    handle_incoming_webmention,
    handle_outgoing_webmentions,
    handle_pending_webmentions,
)
from tests import OptionsTestCase
from tests.util import testfunc


class IncomingWebmentionDelegationTests(OptionsTestCase):
    """INCOMING: Check behaviour of scheduling.handle_incoming_webmention based on settings.WEBMENTIONS_USE_CELERY."""

    def setUp(self) -> None:
        super().setUp()

        obj = testfunc.create_mentionable_object()
        self.source = testfunc.random_url()
        self.target = testfunc.get_absolute_url_for_object(obj)
        self.http_post = QueryDict(f"source={self.source}&target={self.target}")
        self.sent_by = "localhost"

    def test_incoming_with_celery_disabled(self):
        """handle_incoming_webmention creates PendingIncomingWebmention when celery is disabled."""
        self.enable_celery(False)

        handle_incoming_webmention(self.http_post, self.sent_by)

        all_pending = PendingIncomingWebmention.objects.all()
        self.assertEqual(1, all_pending.count())

        pending = all_pending.first()
        self.assertEqual(pending.source_url, self.source)
        self.assertEqual(pending.target_url, self.target)
        self.assertEqual(pending.sent_by, self.sent_by)

    def test_incoming_with_celery_enabled(self):
        """handle_incoming_webmention delegates to celery when it is enabled."""
        self.enable_celery(True)

        with patch(
            "mentions.tasks.incoming.process_incoming_webmention.delay"
        ) as mock_task, patch(
            "mentions.tasks.scheduling._reschedule_handle_pending_webmentions"
        ) as mock_task_two:
            handle_incoming_webmention(self.http_post, self.sent_by)
            self.assertTrue(mock_task.called)
            self.assertTrue(mock_task_two.called)

        pending = PendingIncomingWebmention.objects.all()
        self.assertEqual(0, pending.count())


class OutgoingWebmentionDelegationTests(OptionsTestCase):
    """OUTGOING: Check behaviour of scheduling.handle_outgoing_webmentions based on settings.WEBMENTIONS_USE_CELERY."""

    def setUp(self) -> None:
        super().setUp()

        obj = testfunc.create_mentionable_object("Content that might mention a URL")
        self.absolute_url = obj.get_absolute_url()
        self.all_text = obj.all_text()

    def test_outgoing_with_celery_disabled(self):
        """handle_outgoing_webmentions creates PendingOutgoingContent when celery is disabled."""
        self.enable_celery(False)

        handle_outgoing_webmentions(self.absolute_url, self.all_text)

        all_pending = PendingOutgoingContent.objects.all()
        self.assertEqual(1, all_pending.count())

        pending = all_pending.first()
        self.assertEqual(pending.absolute_url, self.absolute_url)
        self.assertEqual(pending.text, self.all_text)

    def test_outgoing_with_celery_enabled(self):
        """handle_outgoing_webmentions delegates to celery when it is enabled."""
        self.enable_celery(True)

        with patch(
            "mentions.tasks.outgoing.process_outgoing_webmentions.delay"
        ) as mock_task, patch(
            "mentions.tasks.scheduling._reschedule_handle_pending_webmentions"
        ) as mock_task_two:
            handle_outgoing_webmentions(self.absolute_url, self.all_text)
            self.assertTrue(mock_task.called)
            self.assertTrue(mock_task_two.called)

        all_pending = PendingOutgoingContent.objects.all()
        self.assertEqual(0, all_pending.count())


class HandlePendingMentionsTests(OptionsTestCase):
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
