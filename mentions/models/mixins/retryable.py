from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from mentions import options

__all__ = [
    "RetryableMixin",
]


class RetryableMixin(models.Model):
    """A mixin for models that need to track reprocessing attempts."""

    class Meta:
        abstract = True

    retry_attempt_count = models.PositiveSmallIntegerField(
        _("retry attempt count"),
        default=0,
        editable=False,
        help_text=_("How many times we have attempted to process this object."),
    )
    last_retry_attempt = models.DateTimeField(
        _("latest retry attempt"),
        null=True,
        blank=True,
        help_text=_("When we last attempted to process this object."),
    )
    is_awaiting_retry = models.BooleanField(
        _("awaiting retry"),
        default=True,
        help_text=_(
            "Whether this object is eligible for another attempt at processing."
        ),
    )
    is_retry_successful = models.BooleanField(
        _("retry successful"),
        default=False,
        help_text=_("Whether this object has been processed successfully."),
        editable=False,
    )

    def mark_processing_failed(self, save: bool = False, now=timezone.now) -> None:
        if callable(now):
            now = now()

        self.retry_attempt_count += 1
        self.last_retry_attempt = now
        self.is_awaiting_retry = self.retry_attempt_count < options.max_retries()
        self.is_retry_successful = False

        if save:
            self.save()

    def mark_processing_successful(self, save: bool = False, now=timezone.now) -> None:
        if callable(now):
            now = now()

        self.retry_attempt_count += 1
        self.last_retry_attempt = now
        self.is_awaiting_retry = False
        self.is_retry_successful = True

        if save:
            self.save()

    def can_retry(self, now=timezone.now) -> bool:
        """Return True if awaiting_retry and enough time has passed since last_retry_attempt."""

        if self.is_retry_successful:
            return False

        if not self.is_awaiting_retry:
            return False

        if self.retry_attempt_count >= options.max_retries():
            return False

        if self.last_retry_attempt is None:
            return True

        if callable(now):
            now = now()

        seconds_since_last = (now - self.last_retry_attempt).total_seconds()
        return self.is_awaiting_retry and seconds_since_last >= options.retry_interval()

    def reset_retries(self):
        self.retry_attempt_count = 0
        self.is_awaiting_retry = True
        self.is_retry_successful = False
        self.save(
            update_fields=[
                "retry_attempt_count",
                "is_awaiting_retry",
                "is_retry_successful",
            ]
        )
