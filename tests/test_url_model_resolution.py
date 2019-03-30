import logging

from django.test import TestCase
from django.urls import re_path

from mentions.exceptions import BadConfig, TargetDoesNotExist
from mentions.tests import util
from mentions.tests.models import MentionableTestModel
from mentions.tests.util import constants
from mentions.tests.util.urls import urlpatterns as correct_urlpatterns
from mentions.tests.views import AllEndpointsMentionableTestView
from mentions.urls import urlpatterns
from mentions.util import get_model_for_url

log = logging.getLogger(__name__)

# Paths as configured in the local urlpatterns
bad_modelname_key = 'with_bad_kwarg_key'
bad_modelname_value = 'with_bad_kwarg_value'
bad_path = 'some_bad_path'

urlpatterns += correct_urlpatterns + [
    re_path(
        fr'^{bad_modelname_key}/{constants.slug_regex}',
        AllEndpointsMentionableTestView.as_view(),
        kwargs={
            'model_name_with_mistyped_key': constants.model_name,
        },
        name=f'bad_modelname_key_{constants.view_all_endpoints}'),
    re_path(
        fr'^{bad_modelname_value}/{constants.slug_regex}',
        AllEndpointsMentionableTestView.as_view(),
        kwargs={
            'model_name': 'tests.UnresolvableModel',
        },
        name=f'bad_modelname_value_{constants.view_all_endpoints}'),
]


class GetModelForUrlTests(TestCase):
    """Tests for util.get_model_for_url."""

    def setUp(self):
        self.stub_id = 'some-id123'
        self.slug = 'some-slug'

        MentionableTestModel.objects.create(
            stub_id=self.stub_id,
            slug=self.slug).save()

    def test_get_model_for_url__with_unknown_url(self):
        """Ensure that URL with an unrecognised path raises an exception."""
        with self.assertRaises(TargetDoesNotExist):
            get_model_for_url(util.url(constants.view_all_endpoints, bad_path))

    def test_get_model_for_url__with_correct_slug(self):
        """Ensure that reverse url lookup finds the correct object."""
        retrieved_object = get_model_for_url(util.url(constants.correct_config, self.slug))

        self.assertEqual(retrieved_object.stub_id, self.stub_id)

    def test_get_model_for_url__with_unknown_slug(self):
        """Ensure that an unknown slug raises an exception."""
        with self.assertRaises(TargetDoesNotExist):
            get_model_for_url(util.url(constants.correct_config, 'unknown-slug'))

    def test_get_model_for_url__with_bad_model_name_config(self):
        """Ensure urlpatterns is set up correctly. urlpatterns must provide a correct dotted path
        value for `model_name` in its kwargs."""

        # Raise BadConfig if kwargs does not have a key named `model_name`.
        with self.assertRaises(BadConfig):
            get_model_for_url(util.url(bad_modelname_key, self.slug))

        # Raise BadConfig if `model_name` kwarg has bad/unresolvable path.
        with self.assertRaises(BadConfig):
            get_model_for_url(util.url(bad_modelname_value, self.slug))
