from django.utils import timezone
from requests import Timeout

from mentions.models import (
    OutgoingWebmentionStatus,
    PendingIncomingWebmention,
    PendingOutgoingContent,
    Webmention,
)
from mentions.tasks.scheduling import handle_pending_webmentions
from tests.tests.util import snippets, testfunc
from tests.tests.util.mocking import patch_http_get, patch_http_post
from tests.tests.util.testcase import OptionsTestCase

MAX_RETRIES = 5
RETRY_INTERVAL = 5 * 60


def after_retry_interval() -> timezone.datetime:
    """Get a datetime that is in the future"""
    return timezone.now() + timezone.timedelta(seconds=RETRY_INTERVAL + 5)


def throw_timeout(*args, **kwargs):
    raise Timeout("Mocked timeout.")


class RetryNoCeleryTests(OptionsTestCase):
    """Retry tasks"""

    def setUp(self) -> None:
        super().setUp()
        self.enable_celery(False)
        self.set_max_retries(MAX_RETRIES)
        self.set_retry_interval(RETRY_INTERVAL)


class RetryIncomingTests(RetryNoCeleryTests):
    test_func = lambda _: handle_pending_webmentions(incoming=True, outgoing=False)

    def setUp(self) -> None:
        super().setUp()

        self.remote_source = testfunc.random_url()
        self.local_target = testfunc.get_absolute_url_for_object()
        self.pending = PendingIncomingWebmention.objects.create(
            source_url=self.remote_source,
            target_url=self.local_target,
            sent_by=self.remote_source,
        )

    def test_mark_for_retry_on_network_error(self):
        """PendingIncomingWebmention marked to retry later on network error."""
        with patch_http_get(response=throw_timeout):
            self.test_func()

        self.pending.refresh_from_db()
        self.assertEqual(self.pending.retry_attempt_count, 1)
        self.assertFalse(self.pending.is_retry_successful)
        self.assertFalse(self.pending.can_retry(now=timezone.now()))

    def test_mark_complete(self):
        """PendingIncomingWebmention deleted when Webmention creation successful."""
        with patch_http_get(text=snippets.html_with_mentions(self.local_target)):
            self.test_func()

        Webmention.objects.get(
            target_url=self.local_target,
            source_url=self.remote_source,
            validated=True,
        )

        with self.assertRaises(PendingIncomingWebmention.DoesNotExist):
            # Webmention has been generated and pending deleted as no longer needed.
            self.pending.refresh_from_db()


class RetryOutgoingTests(RetryNoCeleryTests):
    test_func = lambda _: handle_pending_webmentions(incoming=False, outgoing=True)

    def setUp(self) -> None:
        super().setUp()
        self.local_source = testfunc.get_absolute_url_for_object()
        self.remote_target = testfunc.random_url()

        self.pending = PendingOutgoingContent.objects.create(
            text=snippets.html_with_mentions(self.remote_target),
            absolute_url=self.local_source,
        )

    def test_make_retryable_on_network_error(self):
        with patch_http_get(response=throw_timeout):
            self.test_func()

        status = self.assert_exists(OutgoingWebmentionStatus)
        self.assertEqual(status.target_url, self.remote_target)
        self.assertEqual(status.source_url, self.local_source)

        self.assertEqual(status.retry_attempt_count, 1)
        self.assertTrue(status.is_awaiting_retry)
        self.assertFalse(status.is_retry_successful)

        with self.assertRaises(PendingOutgoingContent.DoesNotExist):
            # OutgoingWebmentionStatus replaces PendingOutgoingContent.
            self.pending.refresh_from_db()

    def test_mark_complete(self):
        with patch_http_get(
            text=snippets.html_with_mentions(self.local_source)
        ), patch_http_post(status_code=202):
            self.test_func()

        status = self.assert_exists(OutgoingWebmentionStatus)
        self.assertEqual(status.retry_attempt_count, 1)
        self.assertFalse(status.is_awaiting_retry)
        self.assertTrue(status.is_retry_successful)

        with self.assertRaises(PendingOutgoingContent.DoesNotExist):
            # OutgoingWebmentionStatus replaces PendingOutgoingContent.
            self.pending.refresh_from_db()

    def test_success_on_retry(self):
        self.set_retry_interval(0)

        with patch_http_get(response=throw_timeout):
            for n in range(3):
                self.test_func()

        with patch_http_get(
            text=snippets.html_with_mentions(self.local_source)
        ), patch_http_post(status_code=202):
            self.test_func()

        status = self.assert_exists(OutgoingWebmentionStatus)
        self.assertTrue(status.is_retry_successful)
        self.assertFalse(status.is_awaiting_retry)
        self.assertEqual(status.retry_attempt_count, 4)

    def test_outgoing_reused(self):
        """Ensure that the correct status is updated. Check for #43."""
        OutgoingWebmentionStatus.objects.create(
            source_url=self.local_source,
            target_url=self.remote_target,
            is_awaiting_retry=False,
        )
        OutgoingWebmentionStatus.objects.create(
            source_url=self.local_source,
            target_url=self.remote_target,
            is_awaiting_retry=True,  # This one should be updated.
        )
        OutgoingWebmentionStatus.objects.create(
            source_url=self.local_source,
            target_url=self.remote_target,
            is_awaiting_retry=False,
        )

        self.set_retry_interval(0)

        with patch_http_get(response=throw_timeout):
            for n in range(3):
                self.test_func()

        with patch_http_get(
            text=snippets.html_with_mentions(self.local_source)
        ), patch_http_post(status_code=202):
            self.test_func()

        self.assertFalse(
            OutgoingWebmentionStatus.objects.filter(is_awaiting_retry=True).exists()
        )
