from mentions.helpers.urls import mentions_path, mentions_re_path
from tests import SimpleTestCase
from tests.models import MentionableTestModel
from tests.views import AllEndpointsMentionableTestView


class HelperPathTests(SimpleTestCase):
    def test_mentions_path_definition(self):
        path_def = mentions_path(
            "with_helper_config/<int:arbitrary_id>",
            AllEndpointsMentionableTestView.as_view(),
            model_class=MentionableTestModel,
            model_field_mapping={
                "arbitrary_id": "id",
            },
        )

        self.assertEqual(
            path_def.default_args["model_name"],
            "tests.MentionableTestModel",
        )

        self.assertEqual(
            path_def.default_args["model_field_mapping"]["arbitrary_id"],
            "id",
        )

    def test_mentions_re_path_definition(self):
        path_def = mentions_re_path(
            r"with_helper_config/<int:arbitrary_id>/",
            AllEndpointsMentionableTestView.as_view(),
            model_class=MentionableTestModel,
            model_field_mapping={
                "arbitrary_id": "id",
            },
        )

        self.assertEqual(
            path_def.default_args["model_name"],
            "tests.MentionableTestModel",
        )

        self.assertEqual(
            path_def.default_args["model_field_mapping"]["arbitrary_id"],
            "id",
        )
