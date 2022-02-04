from unittest.mock import patch

from django.conf import settings
from django.http import QueryDict

from mentions.models import PendingIncomingWebmention, PendingOutgoingContent
from mentions.tasks.scheduling import (
    handle_incoming_webmention,
    handle_outgoing_webmentions,
    handle_pending_webmentions,
)
from tests import WebmentionTestCase
from tests.util import testfunc


class _BaseTestCase(WebmentionTestCase):
    def setUp(self) -> None:
        # Remember default setting value so we can restore it in tearDown.
        self.default_celery = settings.WEBMENTIONS_USE_CELERY

    def tearDown(self) -> None:
        super().tearDown()
        # Restore celery setting to default
        settings.WEBMENTIONS_USE_CELERY = self.default_celery


class IncomingWebmentionDelegationTests(_BaseTestCase):
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
        settings.WEBMENTIONS_USE_CELERY = False

        handle_incoming_webmention(self.http_post, self.sent_by)

        all_pending = PendingIncomingWebmention.objects.all()
        self.assertEqual(1, all_pending.count())

        pending = all_pending.first()
        self.assertEqual(pending.source_url, self.source)
        self.assertEqual(pending.target_url, self.target)
        self.assertEqual(pending.sent_by, self.sent_by)

    def test_incoming_with_celery_enabled(self):
        """handle_incoming_webmention delegates to celery when it is enabled."""
        settings.WEBMENTIONS_USE_CELERY = True

        with patch("mentions.tasks.process_incoming_webmention.delay") as mock_task:
            handle_incoming_webmention(self.http_post, self.sent_by)
            self.assertTrue(mock_task.called)

        pending = PendingIncomingWebmention.objects.all()
        self.assertEqual(0, pending.count())


class OutgoingWebmentionDelegationTests(_BaseTestCase):
    """OUTGOING: Check behaviour of scheduling.handle_outgoing_webmentions based on settings.WEBMENTIONS_USE_CELERY."""

    def setUp(self) -> None:
        super().setUp()

        obj = testfunc.create_mentionable_object("Content that might mention a URL")
        self.absolute_url = obj.get_absolute_url()
        self.all_text = obj.all_text()

    def test_outgoing_with_celery_disabled(self):
        """handle_outgoing_webmentions creates PendingOutgoingContent when celery is disabled."""
        settings.WEBMENTIONS_USE_CELERY = False

        handle_outgoing_webmentions(self.absolute_url, self.all_text)

        all_pending = PendingOutgoingContent.objects.all()
        self.assertEqual(1, all_pending.count())

        pending = all_pending.first()
        self.assertEqual(pending.absolute_url, self.absolute_url)
        self.assertEqual(pending.text, self.all_text)

    def test_outgoing_with_celery_enabled(self):
        """handle_outgoing_webmentions delegates to celery when it is enabled."""
        settings.WEBMENTIONS_USE_CELERY = True

        with patch("mentions.tasks.process_outgoing_webmentions.delay") as mock_task:
            handle_outgoing_webmentions(self.absolute_url, self.all_text)
            self.assertTrue(mock_task.called)

        all_pending = PendingOutgoingContent.objects.all()
        self.assertEqual(0, all_pending.count())


class HandlePendingMentionsTests(_BaseTestCase):
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
        """PendingIncomingWebmentions are passed to process_incoming_webmention, then deleted."""
        with patch(
            "mentions.tasks.scheduling.process_incoming_webmention"
        ) as incoming_task, patch(
            "mentions.tasks.scheduling.process_outgoing_webmentions"
        ) as outgoing_task:
            handle_pending_webmentions(incoming=True, outgoing=False)
            self.assertTrue(incoming_task.called)
            self.assertFalse(outgoing_task.called)

        self.assertEqual(0, PendingIncomingWebmention.objects.all().count())
        self.assertEqual(1, PendingOutgoingContent.objects.all().count())

    def test_handle_pending_outgoing_content(self):
        """PendingOutgoingContent are passed to process_outgoing_webmentions, then deleted."""
        with patch(
            "mentions.tasks.scheduling.process_outgoing_webmentions"
        ) as outgoing_task, patch(
            "mentions.tasks.scheduling.process_incoming_webmention"
        ) as incoming_task:
            handle_pending_webmentions(incoming=False, outgoing=True)
            self.assertTrue(outgoing_task.called)
            self.assertFalse(incoming_task.called)

        self.assertEqual(0, PendingOutgoingContent.objects.all().count())
        self.assertEqual(1, PendingIncomingWebmention.objects.all().count())
