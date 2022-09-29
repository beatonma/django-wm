from django.conf import settings
from django.test import TestCase

from mentions import options


class WebmentionTestCase(TestCase):
    def tearDown(self) -> None:
        super().tearDown()
        from mentions.models import (
            HCard,
            OutgoingWebmentionStatus,
            PendingIncomingWebmention,
            PendingOutgoingContent,
            SimpleMention,
            Webmention,
        )
        from tests.models import (
            BadTestModelMissingAllText,
            BadTestModelMissingGetAbsoluteUrl,
            MentionableTestBlogPost,
            MentionableTestModel,
            SampleBlog,
        )

        app_models = [
            Webmention,
            OutgoingWebmentionStatus,
            PendingIncomingWebmention,
            PendingOutgoingContent,
            HCard,
            SimpleMention,
        ]
        test_models = [
            MentionableTestModel,
            BadTestModelMissingAllText,
            BadTestModelMissingGetAbsoluteUrl,
            MentionableTestBlogPost,
            SampleBlog,
        ]

        all_models = [*app_models, *test_models]
        for Model in all_models:
            Model.objects.all().delete()


class OptionsTestCase(WebmentionTestCase):
    """A TestCase that gracefully handles changes in django-wm options.

    Any options that are changed during a test will be reset to the value
    defined in global settings once the test is done."""

    def setUp(self) -> None:
        self.defaults = options.get_config()

    def tearDown(self) -> None:
        super().tearDown()
        for key, value in self.defaults.items():
            setattr(settings, key, value)

    def enable_celery(self, enable: bool):
        setattr(settings, options.SETTING_USE_CELERY, enable)

    def set_max_retries(self, n: int):
        setattr(settings, options.SETTING_MAX_RETRIES, n)

    def set_retry_interval(self, seconds: int):
        setattr(settings, options.SETTING_RETRY_INTERVAL, seconds)

    def set_dashboard_public(self, public: bool):
        setattr(settings, options.SETTING_DASHBOARD_PUBLIC, public)


class MockResponse:
    """Mock of requests.Response."""

    def __init__(
        self,
        url: str,
        headers: dict = None,
        text: str = None,
        status_code: int = None,
    ):
        self.url = url
        self.text = text
        self.status_code = status_code
        self.headers = headers
