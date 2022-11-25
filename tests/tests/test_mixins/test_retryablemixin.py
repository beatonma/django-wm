from django.utils import timezone

from mentions.models import PendingIncomingWebmention
from mentions.models.mixins import RetryableMixin
from tests.tests.util import testfunc
from tests.tests.util.testcase import OptionsTestCase

MAX_RETRIES = 5
RETRY_INTERVAL = 10 * 60
T1 = timezone.datetime(year=2022, month=8, day=10, hour=11, minute=0, second=0)
T_TOO_SOON = T1 + timezone.timedelta(seconds=RETRY_INTERVAL - 5)
T_CAN_RETRY = T1 + timezone.timedelta(seconds=RETRY_INTERVAL + 5)


def _create_obj() -> RetryableMixin:
    remote_source = testfunc.random_url()
    local_target = testfunc.get_absolute_url_for_object()
    return PendingIncomingWebmention(
        source_url=remote_source,
        target_url=local_target,
        sent_by=remote_source,
    )


class RetryableMixinTests(OptionsTestCase):
    """MODELS: RetryableMixin tests"""

    def setUp(self) -> None:
        super().setUp()
        self.set_max_retries(MAX_RETRIES)
        self.set_retry_interval(RETRY_INTERVAL)

    def test_default_values(self):
        """Default field values are correct."""
        obj = _create_obj()

        self.assertTrue(obj.can_retry())
        self.assertTrue(obj.is_awaiting_retry)
        self.assertFalse(obj.is_retry_successful, False)
        self.assertIsNone(obj.last_retry_attempt)
        self.assertEqual(obj.retry_attempt_count, 0)

    def test_after_failure(self):
        """After few retries, values are correct."""
        obj = _create_obj()
        obj.mark_processing_failed(now=T1)

        self.assertTrue(obj.is_awaiting_retry)
        self.assertFalse(obj.is_retry_successful)
        self.assertIsNotNone(obj.last_retry_attempt)
        self.assertEqual(obj.retry_attempt_count, 1)
        self.assertTrue(obj.can_retry(now=T_CAN_RETRY))

    def test_after_all_failures(self):
        """After options.max_retries reached, values are correct."""
        obj = _create_obj()
        for _ in range(0, MAX_RETRIES):
            obj.mark_processing_failed(now=T1)

        self.assertFalse(obj.is_awaiting_retry)
        self.assertFalse(obj.is_retry_successful)
        self.assertEqual(obj.retry_attempt_count, MAX_RETRIES)
        self.assertFalse(obj.can_retry(now=T_CAN_RETRY))

    def test_can_retry(self):
        """`can_retry()` behaviour is correct."""
        obj = _create_obj()
        self.assertTrue(obj.can_retry(now=T1))

        obj = _create_obj()
        obj.mark_processing_failed(now=T1)

        self.assertFalse(obj.can_retry(now=T_TOO_SOON))
        self.assertTrue(obj.can_retry(now=T_CAN_RETRY))

        obj = _create_obj()
        obj.mark_processing_successful()
        self.assertFalse(obj.can_retry(now=T_TOO_SOON))
        self.assertFalse(obj.can_retry(now=T_CAN_RETRY))
