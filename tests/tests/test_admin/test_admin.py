from typing import Type

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.test.utils import override_settings
from django.urls import path, reverse

from mentions.apps import MentionsConfig
from mentions.models import HCard, SimpleMention, Webmention
from tests.config.urls import core_urlpatterns
from tests.tests.util import testfunc
from tests.tests.util.testcase import WebmentionTestCase

urlpatterns = [
    *core_urlpatterns,
    path(f"{testfunc.random_str()}/", admin.site.urls),
]


def admin_url(model_class: Type[models.Model]) -> str:
    return reverse(
        f"admin:{MentionsConfig.name}_{model_class._meta.model_name}_changelist"
    )


def admin_search_url(model_class: Type[models.Model], query: str) -> str:
    return f"{admin_url(model_class)}?q={query}"


def admin_instance_url(instance: models.Model) -> str:
    return reverse(
        f"admin:{MentionsConfig.name}_{instance._meta.model_name}_change",
        args=[instance.pk],
    )


@override_settings(
    ROOT_URLCONF=__name__,
    STATIC_URL="/static/",
)
class AdminTests(WebmentionTestCase):
    def assert_results(self, url: str, contains: str = None, not_contains: str = None):
        response = self.client.get(url)
        if contains is None and not_contains is None:
            raise Exception(
                "assert_results should provide at least one of (contains|not_contains) args"
            )

        if contains is not None:
            self.assertContains(response, contains)
        if not_contains is not None:
            self.assertNotContains(response, not_contains)

    def setUp(self) -> None:
        user = User.objects.create_superuser(
            username="super",
        )
        self.client.force_login(user)

        self.hcard_one = testfunc.create_hcard()
        self.hcard_two = testfunc.create_hcard()

        self.mention_one = testfunc.create_webmention(hcard=self.hcard_one)
        self.mention_two = testfunc.create_webmention()

        self.simple = testfunc.create_simple_mention()


class AdminChangelistTests(AdminTests):
    def test_changelist(self):
        """Model list renders correctly."""
        for model in testfunc.mentions_model_classes():
            url = admin_url(model)
            with self.subTest(model=model, url=url):
                response = self.client.get(url)
                self.assertEqual(200, response.status_code)

    def test_search_generic(self):
        """Test that model list with a search query renders correctly."""
        for model in testfunc.mentions_model_classes():
            url = admin_search_url(model, query="whatever")
            with self.subTest(model=model, url=url):
                response = self.client.get(url)
                self.assertEqual(200, response.status_code)

    def test_search_hcard(self):
        self.assert_results(
            admin_search_url(HCard, query=self.hcard_one.name),
            contains=self.hcard_one.homepage,
            not_contains=self.hcard_two.homepage,
        )

        self.assert_results(
            admin_search_url(HCard, query=self.hcard_two.homepage),
            contains=self.hcard_two.name,
            not_contains=self.hcard_one.name,
        )

    def test_search_simple(self):
        self.assert_results(
            admin_search_url(SimpleMention, query=self.simple.quote),
            contains=self.simple.source_url,
        )
        self.assert_results(
            admin_search_url(SimpleMention, query="unrelated"),
            not_contains=self.simple.source_url,
        )

    def test_search_webmention(self):
        with self.subTest(msg="Search by hcard name"):
            self.assert_results(
                admin_search_url(Webmention, query=self.hcard_one.name),
                contains=self.mention_one.source_url,
                not_contains=self.mention_two.source_url,
            )

        with self.subTest(msg="Search by hcard homepage"):
            self.assert_results(
                admin_search_url(Webmention, query=self.hcard_one.homepage),
                contains=self.mention_one.source_url,
                not_contains=self.mention_two.source_url,
            )

        with self.subTest(msg="Search by source_url"):
            self.assert_results(
                admin_search_url(Webmention, query=self.mention_two.source_url),
                contains=self.mention_two.source_url,
                not_contains=self.mention_one.source_url,
            )

        with self.subTest(msg="Search by target_url"):
            self.assert_results(
                admin_search_url(Webmention, query=self.mention_one.target_url),
                contains=self.mention_one.target_url,
            )

        with self.subTest(msg="Search by quote"):
            self.assert_results(
                admin_search_url(Webmention, query=self.mention_two.quote),
                contains=self.mention_two.source_url,
                not_contains=self.mention_one.source_url,
            )


class AdminInstanceTests(AdminTests):
    def assert_instance_page_accessible(self, instance: models.Model):
        url = admin_instance_url(instance)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code, msg=f"url={url}")

    def test_webmention_instance(self):
        self.assert_instance_page_accessible(self.mention_one)
        self.assert_instance_page_accessible(self.mention_two)

    def test_simplemention_instance(self):
        self.assert_instance_page_accessible(self.simple)

    def test_hcard_instance(self):
        self.assert_instance_page_accessible(self.hcard_one)
        self.assert_instance_page_accessible(self.hcard_two)

    def test_outgoing_status_instance(self):
        self.assert_instance_page_accessible(testfunc.create_outgoing_status())

    def test_pending_incoming_instance(self):
        self.assert_instance_page_accessible(testfunc.create_pending_incoming())

    def test_pending_outgoing_instance(self):
        self.assert_instance_page_accessible(testfunc.create_pending_outgoing())
