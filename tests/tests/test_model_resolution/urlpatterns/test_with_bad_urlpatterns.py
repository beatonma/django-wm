import logging

from django.test.utils import override_settings
from django.urls import path

from mentions import resolution
from mentions.exceptions import BadUrlConfig, NoModelForUrlPath
from tests.test_app.views import AllEndpointsMentionableTestView
from tests.tests.util import constants, testfunc
from tests.tests.util.testcase import WebmentionTestCase

log = logging.getLogger(__name__)

bad_modelname_key = "with_bad_kwarg_key"
bad_modelname_value = "with_bad_kwarg_value"


urlpatterns = [
    path(
        rf"{bad_modelname_key}/<int:object_id>",
        AllEndpointsMentionableTestView.as_view(),
        kwargs={
            "model_name_with_mistyped_or_missing_key": constants.model_name,
        },
    ),
    path(
        rf"{bad_modelname_value}/<int:object_id>",
        AllEndpointsMentionableTestView.as_view(),
        kwargs={
            "model_name": "tests.UnresolvableModel",
        },
    ),
]


@override_settings(ROOT_URLCONF=__name__)
class GetModelForUrlPathWithBadConfigTests(WebmentionTestCase):
    """INCOMING: Tests for get_model_for_url when there are errors in `urlpatterns` configuration."""

    @classmethod
    def _urlpath(self, path: str, slug: str) -> str:
        return f"/{path}/{slug}"

    def setUp(self) -> None:
        self.target = testfunc.create_mentionable_object()
        super().setUp()

    def test_get_model_for_url__with_bad_model_name_config(self):
        """urlpatterns with no entry for model_name in path kwargs raises NoModelForUrlPath exception."""
        with self.assertRaises(NoModelForUrlPath):
            resolution.get_model_for_url(
                self._urlpath(bad_modelname_key, self.target.pk)
            )

    def test_get_model_for_url__raises_badconfig_when_model_name_unresolvable(self):
        """Unresolvable model_name raises BadUrlConfig exception."""
        with self.assertRaises(BadUrlConfig):
            resolution.get_model_for_url(
                self._urlpath(bad_modelname_value, self.target.pk)
            )
