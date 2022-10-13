from django.urls import reverse

from mentions.helpers.urls import mentions_path
from mentions.resolution import get_model_for_url
from tests import SimpleTestCase
from tests.models import HelperMentionableTestModel, MentionableTestModel
from tests.util import testfunc, viewname
from tests.views import AllEndpointsMentionableTestView


class UrlHelperTests(SimpleTestCase):
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

    def test_mentions_path_view_is_accessible(self):
        obj = HelperMentionableTestModel.objects.create()

        response = self.client.get(
            reverse(viewname.helper_with_target_object_view, args=[obj.id])
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            obj,
            get_model_for_url(testfunc.get_absolute_url_for_object(obj)),
        )
