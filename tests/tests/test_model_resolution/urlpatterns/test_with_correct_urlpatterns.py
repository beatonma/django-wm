from mentions import resolution
from mentions.exceptions import TargetDoesNotExist
from tests.tests.util import testfunc
from tests.tests.util.testcase import WebmentionTestCase


class GetModelForUrlPathTests(WebmentionTestCase):
    """INCOMING: Tests for get_model_for_url_path with correct `urlpatterns` configuration."""

    def test_get_model_for_url__with_correct_slug(self):
        """Reverse URL lookup finds the correct object."""
        target = testfunc.create_mentionable_object()
        retrieved_object = resolution.get_model_for_url(target.get_absolute_url())

        self.assertEqual(retrieved_object.pk, target.pk)

    def test_get_model_for_url__with_unknown_url(self):
        """URL with an unrecognised path raises TargetDoesNotExist exception."""
        with self.assertRaises(TargetDoesNotExist):
            resolution.get_model_for_url("/some/nonexistent/urlpath")
