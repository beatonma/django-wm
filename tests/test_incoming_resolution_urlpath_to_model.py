import logging

from django.urls import path

from mentions import resolution
from mentions.exceptions import BadConfig, TargetDoesNotExist
from tests import WebmentionTestCase
from tests.util import constants, testfunc
from tests.views import AllEndpointsMentionableTestView

log = logging.getLogger(__name__)

# Paths as configured in local_urlpatterns
bad_modelname_key = "with_bad_kwarg_key"
bad_modelname_value = "with_bad_kwarg_value"
bad_path = "some_unresolvable_slug"

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
]


class _BaseTestCase(WebmentionTestCase):
    def setUp(self):
        _create_mentionable_objects()
        self.target = testfunc.create_mentionable_object()
        _create_mentionable_objects()


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


class GetModelForUrlPathWithBadConfigTests(_BaseTestCase):
    """INCOMING: Tests for get_model_for_url_path when there are errors in `urlpatterns` configuration."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from tests.config.test_urls import urlpatterns

        urlpatterns += local_urlpatterns

    def test_get_model_for_url__with_bad_model_name_config(self):
        """urlpatterns with no entry for model_name in path kwargs raises BadConfig exception."""
        with self.assertRaises(BadConfig):
            resolution.get_model_for_url_path(
                _urlpath(bad_modelname_key, self.target.slug)
            )

    def test_get_model_for_url__raises_badconfig_when_model_name_unresolvable(self):
        """Unresolvable model_name raises BadConfig exception."""
        with self.assertRaises(BadConfig):
            resolution.get_model_for_url_path(
                _urlpath(bad_modelname_value, self.target.slug)
            )

    @classmethod
    def tearDownClass(cls) -> None:
        from tests.config.test_urls import urlpatterns

        for x in local_urlpatterns:
            urlpatterns.remove(x)

        super().tearDownClass()


def _urlpath(path: str, slug: str) -> str:
    return f"/{path}/{slug}"


def _create_mentionable_objects(n: int = 3):
    """Create some arbitrary mentionable objects for noise."""

    for x in range(n):
        testfunc.create_mentionable_object()
