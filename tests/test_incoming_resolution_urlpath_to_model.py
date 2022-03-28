import logging

from django.urls import path, register_converter
from django.utils import timezone

from mentions import resolution
from mentions.exceptions import BadConfig, TargetDoesNotExist
from tests import WebmentionTestCase
from tests.models import MentionableTestBlogPost, SampleBlog
from tests.util import constants, testfunc
from tests.views import AllEndpointsMentionableTestView, BlogPostView

log = logging.getLogger(__name__)

# Paths as configured in local_urlpatterns
bad_modelname_key = "with_bad_kwarg_key"
bad_modelname_value = "with_bad_kwarg_value"
bad_path = "some_unresolvable_slug"


class TwoDigitConverter:
    "Matches 2 digits."
    regex = r"[0-9]{2}"

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return f"{int(value):02d}"


register_converter(TwoDigitConverter, "mm")

"""Url patterns that are only used for tests in this file.
Should be added to test_urls.urlpatterns in setUp and removed again in tearDown."""
local_urlpatterns = [
    path(
        fr"{bad_modelname_key}/<slug:slug>",
        AllEndpointsMentionableTestView.as_view(),
        kwargs={
            "model_name_with_mistyped_or_missing_key": constants.model_name,
        },
    ),
    path(
        fr"{bad_modelname_value}/<slug:slug>",
        AllEndpointsMentionableTestView.as_view(),
        kwargs={
            "model_name": "tests.UnresolvableModel",
        },
    ),
    path(
        fr"<slug:blog_slug>/<int:year>/<mm:month>/<int:day>/<slug:post_slug>/",
        BlogPostView.as_view(),
        kwargs={
            "model_name": constants.model_name_test_blogpost,
        },
    ),
]


class _BaseTestCase(WebmentionTestCase):
    def setUp(self):
        _create_mentionable_objects()
        self.target = testfunc.create_mentionable_object()
        _create_mentionable_objects()


class _BaseLocalUrlpatternsTestCase(_BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from tests.config.test_urls import urlpatterns

        urlpatterns += local_urlpatterns

    @classmethod
    def tearDownClass(cls) -> None:
        from tests.config.test_urls import urlpatterns

        for x in local_urlpatterns:
            urlpatterns.remove(x)

        super().tearDownClass()


class GetModelForUrlPathTests(_BaseTestCase):
    """INCOMING: Tests for get_model_for_url_path with correct `urlpatterns` configuration."""

    def test_get_model_for_url__with_correct_slug(self):
        """Reverse URL lookup finds the correct object."""
        retrieved_object = resolution.get_model_for_url_path(
            self.target.get_absolute_url()
        )

        self.assertEqual(retrieved_object.pk, self.target.pk)

    def test_get_model_for_url__with_unknown_url(self):
        """URL with an unrecognised path raises TargetDoesNotExist exception."""
        with self.assertRaises(TargetDoesNotExist):
            resolution.get_model_for_url_path("/some/nonexistent/urlpath")


class GetModelForUrlPathWithBadConfigTests(_BaseLocalUrlpatternsTestCase):
    """INCOMING: Tests for get_model_for_url_path when there are errors in `urlpatterns` configuration."""

    @classmethod
    def _urlpath(self, path: str, slug: str) -> str:
        return f"/{path}/{slug}"

    def test_get_model_for_url__with_bad_model_name_config(self):
        """urlpatterns with no entry for model_name in path kwargs raises BadConfig exception."""
        with self.assertRaises(BadConfig):
            resolution.get_model_for_url_path(
                self._urlpath(bad_modelname_key, self.target.slug)
            )

    def test_get_model_for_url__raises_badconfig_when_model_name_unresolvable(self):
        """Unresolvable model_name raises BadConfig exception."""
        with self.assertRaises(BadConfig):
            resolution.get_model_for_url_path(
                self._urlpath(bad_modelname_value, self.target.slug)
            )


class GetModelForUrlWithCustomObjectResolution(_BaseLocalUrlpatternsTestCase):
    """INCOMING: Tests for get_model_for_url_path when MentionableMixin.resolve_from_url_kwargs has been overridden."""

    def setUp(self) -> None:
        self.published = timezone.datetime(2022, 3, 28, 9, 3, 2)

        blog = SampleBlog.objects.create(slug="blogslug")
        MentionableTestBlogPost.objects.create(
            blog=blog,
            content="hello am decoy",
            slug="testpostdecoyslug",
            timestamp=self.published,
        )
        self.blogpost = MentionableTestBlogPost.objects.create(
            blog=blog,
            content="hello am blog",
            slug="testpostslug",
            timestamp=self.published,
        )
        MentionableTestBlogPost.objects.create(
            blog=blog,
            content="hello am decoy",
            slug="testpostslug",
            timestamp=timezone.datetime(2022, 3, 27, 9, 3, 2),
        )

    def test_get_model_for_url__with_custom_lookup(self):
        """Reverse URL lookup with custom resolve_from_url_kwargs implementation finds the correct object."""
        retrieved_object = resolution.get_model_for_url_path(
            "/blogslug/2022/03/28/testpostslug/"
        )

        self.assertEqual(retrieved_object, self.blogpost)


def _create_mentionable_objects(n: int = 3):
    """Create some arbitrary mentionable objects for noise."""

    for x in range(n):
        testfunc.create_mentionable_object()
