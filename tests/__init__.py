import logging
from typing import Callable, Optional, Type, TypeVar, Union
from unittest.mock import Mock, patch

import requests
from django.conf import settings
from django.db import models
from django.db.models import QuerySet
from django.test import TestCase
from requests.structures import CaseInsensitiveDict

from mentions import options

log = logging.getLogger(__name__)

M = TypeVar("M", bound=models.Model)


class SimpleTestCase(TestCase):
    pass


class WebmentionTestCase(SimpleTestCase):
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

    def assert_exists(
        self,
        model_class: Type[M],
        count: int = 1,
        **query,
    ) -> Union[M, QuerySet[M]]:
        """Assert that the expected number of model instances exist and return it/them."""
        if count == 1:
            try:
                return model_class.objects.get(**query)
            except (model_class.DoesNotExist, model_class.MultipleObjectsReturned) as e:
                raise AssertionError(f"Expected 1 instance of {model_class}: {e}")

        qs = model_class.objects.filter(**query)
        self.assertEqual(count, qs.count())
        return qs

    def assert_not_exists(self, model_class: Type[M], **query):
        qs = model_class.objects.filter(**query)
        self.assertFalse(
            qs.exists(),
            msg=f"Model {model_class.__name__} with query={query} should not exist: {qs}",
        )


class OptionsTestCase(WebmentionTestCase):
    """A TestCase that gracefully handles changes in django-wm options.

    Any options that are changed during a test will be reset to the value
    defined in global settings once the test is done."""

    def setUp(self) -> None:
        super().setUp()
        self.defaults = options.get_config()

    def tearDown(self) -> None:
        super().tearDown()
        for key, value in self.defaults.items():
            setattr(settings, key, value)

        if hasattr(settings, options.NAMESPACE):
            delattr(settings, options.NAMESPACE)

    def enable_celery(self, enable: bool):
        setattr(settings, options.SETTING_USE_CELERY, enable)

    def set_max_retries(self, n: int):
        setattr(settings, options.SETTING_MAX_RETRIES, n)

    def set_retry_interval(self, seconds: int):
        setattr(settings, options.SETTING_RETRY_INTERVAL, seconds)

    def set_dashboard_public(self, public: bool):
        setattr(settings, options.SETTING_DASHBOARD_PUBLIC, public)

    def set_incoming_target_model_required(self, requires_model: bool):
        setattr(
            settings,
            options.SETTING_INCOMING_TARGET_MODEL_REQUIRED,
            requires_model,
        )

    def set_allow_self_mentions(self, allow: bool):
        setattr(settings, options.SETTING_ALLOW_SELF_MENTIONS, allow)


class MockResponse:
    """Mock of requests.Response."""

    url: str
    headers: Optional[CaseInsensitiveDict]
    text: Optional[str]
    status_code: Optional[int]

    def __init__(
        self,
        url: str,
        headers: Optional[dict] = None,
        text: Optional[str] = None,
        status_code: Optional[int] = None,
    ):
        self.url = url
        self.text = text
        self.status_code = status_code
        self.headers = CaseInsensitiveDict(headers or {"Content-Type": "text/html"})
        log.debug(self)

    def __str__(self):
        return f"[{self.status_code}] {self.url}"


def patch_http_get(
    status_code: int = 200,
    text: Optional[str] = None,
    headers: Optional[dict] = None,
    response: Optional[Callable] = None,
):
    headers = headers or {"content-type": "text/html"}

    side_effect = (
        response
        if response
        else lambda url, **kw: MockResponse(
            url,
            headers=headers,
            text=text or "",
            status_code=status_code,
        )
    )

    return patch.object(
        requests,
        "get",
        Mock(side_effect=side_effect),
    )


def patch_http_post(
    status_code: int = 200,
    headers: Optional[dict] = None,
    response: Optional[Callable] = None,
):
    side_effect = (
        response
        if response
        else lambda url, **kw: MockResponse(
            url,
            headers=headers,
            status_code=status_code,
        )
    )

    return patch.object(
        requests,
        "post",
        Mock(side_effect=side_effect),
    )
