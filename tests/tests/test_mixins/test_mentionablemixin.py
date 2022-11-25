from mentions.exceptions import ImplementationRequired
from tests.test_app.models import (
    BadTestModelMissingAllText,
    BadTestModelMissingGetAbsoluteUrl,
    MentionableTestModel,
)
from tests.tests.util import testfunc
from tests.tests.util.testcase import WebmentionTestCase


def _create_model_instance(Model):
    return Model.objects.create(content=testfunc.random_str())


class MentionableMixinImplementationTests(WebmentionTestCase):
    """MODELS: MentionableMixin implementation tests."""

    def test_correct_implementation(self):
        """Basic MentionableMixin implementation works correctly."""
        obj = _create_model_instance(MentionableTestModel)

        response = self.client.get(obj.get_absolute_url())
        self.assertEqual(200, response.status_code)
        self.assertEqual(obj.get_content_html(), obj.content)

    def test_missing_get_absolute_url(self):
        """Mentionable model that does not override get_absolute_url raises ImplementationRequired exception."""
        obj = _create_model_instance(BadTestModelMissingGetAbsoluteUrl)

        with self.assertRaises(ImplementationRequired):
            obj.get_absolute_url()

    def test_unimplemented_get_content_html(self):
        """Mentionable model that does not override get_content_html raises ImplementationRequired exception."""
        obj = _create_model_instance(BadTestModelMissingAllText)

        with self.assertRaises(ImplementationRequired):
            obj.get_content_html()
