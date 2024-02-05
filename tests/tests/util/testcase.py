from typing import Type, TypeVar, Union

from django.conf import settings
from django.db import models
from django.db.models import QuerySet
from django.test import TestCase
from django.urls import reverse

from mentions import options
from mentions.views import view_names
from tests.tests.util import testfunc

M = TypeVar("M", bound=models.Model)


class SimpleTestCase(TestCase):
    pass


class ClientTestCase(TestCase):
    def get_endpoint_dashboard(self):
        return self.client.get(reverse(view_names.webmention_dashboard))

    def get_endpoint_primary(self):
        return self.client.get(reverse(view_names.webmention_api_incoming))

    def get_endpoint_mentions(self, url: str):
        return self.client.get(
            reverse(view_names.webmention_api_get),
            data={"url": url},
        )

    def get_endpoint_mentions_by_type(self, url: str):
        return self.client.get(
            reverse(view_names.webmention_api_get_by_type),
            data={"url": url},
        )


class WebmentionTestCase(ClientTestCase, SimpleTestCase):
    def tearDown(self) -> None:
        super().tearDown()
        from tests.test_app.models import (
            BadTestModelMissingAllText,
            BadTestModelMissingGetAbsoluteUrl,
            MentionableTestBlogPost,
            MentionableTestModel,
            SampleBlog,
        )

        app_models = testfunc.mentions_model_classes()

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
