from mentions.exceptions import ImplementationRequired
from tests import WebmentionTestCase
from tests.models import (
    BadTestModelMissingAllText,
    BadTestModelMissingGetAbsoluteUrl,
    MentionableTestModel,
)
from tests.util import testfunc


def _create_model_instance(Model):
    pk, slug = testfunc.get_id_and_slug()

    return Model.objects.create(
        pk=pk,
        slug=slug,
        content=testfunc.random_domain(),
    )


class MentionableMixinImplementationTests(WebmentionTestCase):
    """MODELS: MentionableMixin implementation tests."""

    def test_correct_implementation(self):
        """Basic MentionableMixin implementation works correctly."""
        obj = _create_model_instance(MentionableTestModel)

        response = self.client.get(obj.get_absolute_url())
        self.assertEqual(200, response.status_code)
        self.assertEqual(obj.all_text(), obj.content)

    def test_missing_get_absolute_url(self):
        """Mentionable model that does not override get_absolute_url raises ImplementationRequired exception."""
        obj = _create_model_instance(BadTestModelMissingGetAbsoluteUrl)

        with self.assertRaises(ImplementationRequired):
            obj.get_absolute_url()

    def test_unimplemented_alltext(self):
        """Mentionable model that does not override all_text raises ImplementationRequired exception."""
        obj = _create_model_instance(BadTestModelMissingAllText)

        with self.assertRaises(ImplementationRequired):
            obj.all_text()
