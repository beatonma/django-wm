from unittest.mock import patch

import requests
from django.utils import timezone
from requests import Timeout

from mentions.models import (
    OutgoingWebmentionStatus,
    PendingIncomingWebmention,
    PendingOutgoingContent,
    Webmention,
)
from mentions.tasks.scheduling import handle_pending_webmentions
from tests import MockResponse, OptionsTestCase
from tests.util import snippets, testfunc

MAX_RETRIES = 5
RETRY_INTERVAL = 5 * 60


def after_retry_interval() -> timezone.datetime:
    """Get a datetime that is in the future"""
    return timezone.now() + timezone.timedelta(seconds=RETRY_INTERVAL + 5)


class RetryNoCeleryTests(OptionsTestCase):
    """Retry tasks"""

    def setUp(self) -> None:
        super().setUp()
        self.enable_celery(False)
        self.set_max_retries(MAX_RETRIES)
        self.set_retry_interval(RETRY_INTERVAL)

    def _patched_timeout(self):
        def _timeout_patch(*args, **kwargs):
            raise Timeout("Mocked timeout.")

        return patch.object(requests, "get", _timeout_patch)


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
        with self._patched_timeout():
            self.test_func()

        self.pending.refresh_from_db()
        self.assertEqual(self.pending.retry_attempt_count, 1)
        self.assertFalse(self.pending.is_retry_successful)
        self.assertFalse(self.pending.can_retry(now=timezone.now()))

    def test_mark_complete(self):
        """PendingIncomingWebmention deleted when Webmention creation successful."""
        with self._patched_success():
            self.test_func()

        Webmention.objects.get(
            target_url=self.local_target,
            source_url=self.remote_source,
            validated=True,
        )

        with self.assertRaises(PendingIncomingWebmention.DoesNotExist):
            # Webmention has been generated and pending deleted as no longer needed.
            self.pending.refresh_from_db()

    def _patched_success(self):
        def _success_patch(*args, **kwargs):
            return MockResponse(
                self.remote_source,
                text=snippets.html_with_mentions(self.local_target),
                status_code=200,
                headers={"content-type": "text/html"},
            )

        return patch.object(requests, "get", _success_patch)


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
        with self._patched_timeout():
            self.test_func()

        status: OutgoingWebmentionStatus = OutgoingWebmentionStatus.objects.first()
        self.assertEqual(status.target_url, self.remote_target)
        self.assertEqual(status.source_url, self.local_source)

        self.assertEqual(status.retry_attempt_count, 1)
        self.assertTrue(status.is_awaiting_retry)
        self.assertFalse(status.is_retry_successful)

        with self.assertRaises(PendingOutgoingContent.DoesNotExist):
            # OutgoingWebmentionStatus replaces PendingOutgoingContent.
            self.pending.refresh_from_db()

    def test_mark_complete(self):
        with patch.object(requests, "get", self._success_patch), patch.object(
            requests, "post", self._endpoint_patch
        ):
            self.test_func()

        status: OutgoingWebmentionStatus = OutgoingWebmentionStatus.objects.first()
        self.assertEqual(status.retry_attempt_count, 1)
        self.assertFalse(status.is_awaiting_retry)
        self.assertTrue(status.is_retry_successful)

        with self.assertRaises(PendingOutgoingContent.DoesNotExist):
            # OutgoingWebmentionStatus replaces PendingOutgoingContent.
            self.pending.refresh_from_db()

    def test_success_on_retry(self):
        self.set_retry_interval(0)

        with self._patched_timeout():
            for n in range(3):
                self.test_func()

        with patch.object(requests, "get", self._success_patch), patch.object(
            requests, "post", self._endpoint_patch
        ):
            self.test_func()

        status: OutgoingWebmentionStatus = OutgoingWebmentionStatus.objects.first()
        self.assertTrue(status.is_retry_successful)
        self.assertFalse(status.is_awaiting_retry)
        self.assertEqual(status.retry_attempt_count, 4)

    def _success_patch(self, *args, **kwargs):
        return MockResponse(
            self.remote_target,
            text=snippets.html_with_mentions(self.local_source),
            status_code=200,
            headers={"content-type": "text/html"},
        )

    def _endpoint_patch(self, *args, **kwargs):
        return MockResponse("/webmention/", status_code=202)
