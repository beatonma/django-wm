"""General-purpose views used in multiple tests.

Views for specific test cases should be defined alongside those tests."""

import logging

from django.http import HttpResponse
from django.views.generic.base import View

from tests.test_app.models import MentionableTestModel
from tests.tests.util import snippets, testfunc

log = logging.getLogger(__name__)


class AllEndpointsMentionableTestView(View):
    """A view that is associated with a MentionableTestModel.

    Webmentions are retrieved via the associated model instance."""

    def get(self, request, object_id: int, *args, **kwargs):
        obj = MentionableTestModel.objects.get(id=object_id)
        html = snippets.html_all_endpoints(obj.content)

        response = HttpResponse(html, status=200)
        response["Link"] = snippets.http_header_link(
            testfunc.endpoint_submit_webmention_absolute()
        )
        return response


class SimpleNoObjectTestView(View):
    """A simple view with no associated mentionable object.

    Webmentions should still be able to target this page via its URL."""

    def get(self, request):
        return HttpResponse(snippets.html_all_endpoints("whatever content"), status=200)
