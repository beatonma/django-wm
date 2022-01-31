import logging

from django.urls import re_path

from mentions import util
from mentions.exceptions import BadConfig, TargetDoesNotExist
from mentions.tests import WebmentionTestCase
from mentions.tests.models import MentionableTestModel
from mentions.tests.util import constants, testfunc, viewname
from mentions.tests.views import AllEndpointsMentionableTestView

log = logging.getLogger(__name__)

# Paths as configured in the local urlpatterns
bad_modelname_key = "with_bad_kwarg_key"
bad_modelname_value = "with_bad_kwarg_value"
bad_path = "some_bad_path"

"""Url patterns that are only used for tests in this file.
Should be added to test_urls.urlpatterns in setUp and removed again in tearDown."""
local_urlpatterns = [
    re_path(
        fr"^{bad_modelname_key}/{constants.slug_regex}",
        AllEndpointsMentionableTestView.as_view(),
        kwargs={
            "model_name_with_mistyped_key": constants.model_name,
        },
        name=f"bad_modelname_key_{viewname.with_all_endpoints}",
    ),
    re_path(
        fr"^{bad_modelname_value}/{constants.slug_regex}",
        AllEndpointsMentionableTestView.as_view(),
        kwargs={
            "model_name": "tests.UnresolvableModel",
        },
        name=f"bad_modelname_value_{viewname.with_all_endpoints}",
    ),
]


class GetModelForUrlTests(WebmentionTestCase):
    """Tests for util.get_model_for_url_path."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from mentions.tests.config.test_urls import urlpatterns

        urlpatterns += local_urlpatterns

    def setUp(self):
        self.pk, self.slug = testfunc.get_id_and_slug()

        MentionableTestModel.objects.create(pk=self.pk, slug=self.slug)
        testfunc.create_mentionable_objects()

    def _get_model_for_url_path(self, path, slug):
        return util.get_model_for_url_path(testfunc.url_path(path, slug))

    def test_get_model_for_url__with_unknown_url(self):
        """Ensure that URL with an unrecognised path raises an exception."""
        with self.assertRaises(TargetDoesNotExist):
            self._get_model_for_url_path(viewname.with_all_endpoints, bad_path)

    def test_get_model_for_url__with_correct_slug(self):
        """Ensure that reverse url lookup finds the correct object."""
        retrieved_object = self._get_model_for_url_path(
            constants.correct_config, self.slug
        )

        self.assertEqual(retrieved_object.pk, self.pk)

    def test_get_model_for_url__with_unknown_slug(self):
        """Ensure that an unknown slug raises an TargetDoesNotExist exception."""
        with self.assertRaises(TargetDoesNotExist):
            self._get_model_for_url_path(constants.correct_config, "unknown-slug")

    def test_get_model_for_url__with_bad_model_name_config(self):
        """Ensure that an unresolvable `model_name` (in urlpatterns path) raises BadConfig exception."""

        # Raise BadConfig if kwargs does not have a key named `model_name`.
        with self.assertRaises(BadConfig):
            self._get_model_for_url_path(bad_modelname_key, self.slug)

        # Raise BadConfig if `model_name` kwarg has bad/unresolvable path.
        with self.assertRaises(BadConfig):
            self._get_model_for_url_path(bad_modelname_value, self.slug)

    @classmethod
    def tearDownClass(cls) -> None:
        from mentions.tests.config.test_urls import urlpatterns

        for x in local_urlpatterns:
            urlpatterns.remove(x)

        super().tearDownClass()
