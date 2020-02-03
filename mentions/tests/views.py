"""
Views that are only used for running tests.
"""

import logging

from django.http import HttpResponse
from django.views.generic.base import View

from mentions.tests.util import snippets
from mentions.tests.util import constants
from mentions.tests.models import MentionableTestModel

log = logging.getLogger(__name__)


class AllEndpointsMentionableTestView(View):
    """
    Expose webmention endpoint in HTTP header, HTML HEAD and HTML BODY.
    """

    def dispatch(self, request, *args, **kwargs):
        obj = MentionableTestModel.objects.get(slug=kwargs.get('slug'))
        html = snippets.html_all_endpoints(obj.content)
        response = HttpResponse(html, status=200)
        response['Link'] = snippets.http_header_link(
            constants.webmention_api_absolute_url)
        return response


class SimpleNoObjectTestView(View):
    """
    A simple view with no associated Mentionable object. Should be able to accept
    incoming webmentions but there is no
    """
    def get(self, request):
        return HttpResponse(snippets.html_all_endpoints('whatever content'), status=200)
