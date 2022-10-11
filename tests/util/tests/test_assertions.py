from tests import WebmentionTestCase
from tests.models import MentionableTestModel


class AssertionsTestCase(WebmentionTestCase):
    def test_assert_existence_when_none_exist(self):
        with self.assertRaises(AssertionError):
            self.assert_exists(MentionableTestModel)

        with self.assertRaises(AssertionError):
            self.assert_exists(MentionableTestModel, count=2)

        self.assert_exists(MentionableTestModel, count=0)
        self.assert_not_exists(MentionableTestModel)

        MentionableTestModel.objects.create(slug="obj")
        self.assert_exists(MentionableTestModel)

    def test_assert_existence_when_one_exists(self):
        MentionableTestModel.objects.create(slug="obj")

        self.assert_exists(MentionableTestModel)
        self.assert_exists(MentionableTestModel, slug="obj")

        with self.assertRaises(AssertionError):
            self.assert_not_exists(MentionableTestModel)

        with self.assertRaises(AssertionError):
            self.assert_exists(MentionableTestModel, count=2)

    def test_assert_existence_when_many_exist(self):
        MentionableTestModel.objects.create(slug="one")
        MentionableTestModel.objects.create(slug="two")

        with self.assertRaises(AssertionError):
            self.assert_exists(MentionableTestModel)

        with self.assertRaises(AssertionError):
            self.assert_not_exists(MentionableTestModel, slug="two")

        self.assert_exists(MentionableTestModel, slug="one")
        self.assert_exists(MentionableTestModel, slug="two")

        self.assert_exists(MentionableTestModel, count=2)
