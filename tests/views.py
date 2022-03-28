"""
Views that are only used for running tests.
"""

import logging

from django.http import HttpResponse
from django.views.generic.base import TemplateView, View

from tests.models import MentionableTestBlogPost, MentionableTestModel
from tests.util import snippets, testfunc

log = logging.getLogger(__name__)


class AllEndpointsMentionableTestView(View):
    """A view that is associated with a MentionableTestModel.

    Webmentions are retrieved via the associated model instance."""

    def get(self, request, *args, **kwargs):
        obj = MentionableTestModel.objects.get(slug=kwargs.get("slug"))
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


class TemplateTagTestView(TemplateView):
    """Render page to test `{% webmention_endpoint %}` tag."""

    template_name = "templatetags_example.html"


class BlogPostView(View):
    """A view that is associated with a MentionableTestModel.

    Webmentions are retrieved via the associated model instance."""

    def get(
        self,
        request,
        *args,
        blog_slug: str,
        year: int,
        month: int,
        day: int,
        post_slug: str,
        **kwargs
    ):
        obj = MentionableTestBlogPost.objects.get(
            blog__slug=blog_slug,
            time_published__year=year,
            time_published__month=month,
            time_published__day=day,
            slug=post_slug,
        )
        html = snippets.html_all_endpoints(obj.content)
        response = HttpResponse(html, status=200)
        response["Link"] = snippets.http_header_link(
            testfunc.endpoint_submit_webmention_absolute()
        )
        return response
