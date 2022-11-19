from tests.test_app.models import MentionableTestModel
from tests.tests.util.testcase import WebmentionTestCase


class AssertionsTestCase(WebmentionTestCase):
    def test_assert_existence_when_none_exist(self):
        with self.assertRaises(AssertionError):
            self.assert_exists(MentionableTestModel)

        with self.assertRaises(AssertionError):
            self.assert_exists(MentionableTestModel, count=2)

        self.assert_exists(MentionableTestModel, count=0)
        self.assert_not_exists(MentionableTestModel)

        MentionableTestModel.objects.create(name="obj")
        self.assert_exists(MentionableTestModel)

    def test_assert_existence_when_one_exists(self):
        MentionableTestModel.objects.create(name="obj")

        self.assert_exists(MentionableTestModel)
        self.assert_exists(MentionableTestModel, name="obj")

        with self.assertRaises(AssertionError):
            self.assert_not_exists(MentionableTestModel)

        with self.assertRaises(AssertionError):
            self.assert_exists(MentionableTestModel, count=2)

    def test_assert_existence_when_many_exist(self):
        MentionableTestModel.objects.create(name="one")
        MentionableTestModel.objects.create(name="two")

        with self.assertRaises(AssertionError):
            self.assert_exists(MentionableTestModel)

        with self.assertRaises(AssertionError):
            self.assert_not_exists(MentionableTestModel, name="two")

        self.assert_exists(MentionableTestModel, name="one")
        self.assert_exists(MentionableTestModel, name="two")

        self.assert_exists(MentionableTestModel, count=2)
