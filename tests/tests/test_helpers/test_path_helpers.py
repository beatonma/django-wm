from mentions.helpers.urls import mentions_path, mentions_re_path
from tests.test_app.models import MentionableTestModel
from tests.tests.util.testcase import SimpleTestCase


def viewfunc():
    pass


class HelperPathTests(SimpleTestCase):
    def test_mentions_path_definition(self):
        path_def = mentions_path(
            "with_helper_config/<int:arbitrary_id>",
            viewfunc,
            model_class=MentionableTestModel,
            model_filter_map={
                "arbitrary_id": "id",
            },
            kwargs={
                "something-else": 3,
            },
        )

        self.assertEqual(
            path_def.default_args["model_name"],
            "test_app.MentionableTestModel",
        )

        self.assertEqual(
            path_def.default_args["model_filter_map"]["arbitrary_id"],
            "id",
        )

        self.assertEqual(path_def.default_args["something-else"], 3)

    def test_mentions_path_with_default_mapping(self):
        """If `model_filter_map` is not provided, assume names are same for both view and model."""
        path_def = mentions_path(
            "with_helper_config/<int:id>",
            viewfunc,
            model_class=MentionableTestModel,
            kwargs={
                "something-else": 4,
            },
        )

        kwargs = path_def.default_args
        self.assertEqual(
            kwargs["model_name"],
            "test_app.MentionableTestModel",
        )
        self.assertEqual(kwargs["model_filter_map"], {"id"})
        self.assertEqual(kwargs["something-else"], 4)


class HelperRegexPathTests(SimpleTestCase):
    def test_mentions_re_path_definition(self):
        path_def = mentions_re_path(
            r"with_helper_config/(?P<regex_id>[\w-]+)/",
            viewfunc,
            model_class=MentionableTestModel,
            model_filter_map={
                "regex_id": "id",
            },
            kwargs={"another-thing": "blah"},
        )

        kwargs = path_def.default_args
        self.assertEqual(
            kwargs["model_name"],
            "test_app.MentionableTestModel",
        )

        self.assertEqual(
            kwargs["model_filter_map"]["regex_id"],
            "id",
        )

        self.assertEqual(kwargs["another-thing"], "blah")

    def test_mentions_re_path_with_default_mapping(self):
        """If `model_filter_map` is not provided, assume names are same for both view and model."""
        path_def = mentions_path(
            r"with_helper_config/(?P<id>[\d]+)",
            viewfunc,
            model_class=MentionableTestModel,
        )

        self.assertEqual(path_def.default_args["model_filter_map"], {"id"})
