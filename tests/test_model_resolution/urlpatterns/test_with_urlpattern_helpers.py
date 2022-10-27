from django.http import HttpResponse
from django.test.utils import override_settings
from django.views import View

from mentions.helpers.urls import mentions_path
from mentions.resolution import get_model_for_url
from tests import WebmentionTestCase
from tests.config.test_urls import core_urlpatterns
from tests.models import MentionableTestModel
from tests.util import snippets, testfunc, viewname


class HelperMentionableTestView(View):
    """A view that is associated with a MentionableTestModel.

    Webmentions are retrieved via the associated model instance."""

    def get(self, request, arbitrary_name: int, *args, **kwargs):
        obj = MentionableTestModel.objects.get(id=arbitrary_name)
        html = snippets.html_all_endpoints(obj.content)

        response = HttpResponse(html, status=200)
        response["Link"] = snippets.http_header_link(
            testfunc.endpoint_submit_webmention_absolute()
        )
        return response


urlpatterns = [
    mentions_path(
        "with_helper_config/<int:arbitrary_name>/",
        HelperMentionableTestView.as_view(),
        model_class=MentionableTestModel,
        model_field_mapping={"arbitrary_name": "id"},
        name=viewname.helper_with_target_object_view,
    ),
    *core_urlpatterns,
]


@override_settings(ROOT_URLCONF=__name__)
class UrlpatternsHelperTests(WebmentionTestCase):
    def test_mentions_path_view_is_accessible(self):
        obj = MentionableTestModel.objects.create(
            viewname=viewname.helper_with_target_object_view
        )
        response = self.client.get(obj.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        retrieved_obj = get_model_for_url(testfunc.get_absolute_url_for_object(obj))
        self.assertEqual(obj, retrieved_obj)
