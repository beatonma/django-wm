"""
Views that are only used for running tests.
"""

import logging

from django.http import HttpResponse
from django.views.generic.base import View

import mentions.tests.util.snippets
from mentions.tests.util import constants
from .models import MentionableTestModel

log = logging.getLogger(__name__)


class AllEndpointsMentionableTestView(View):
    """
    Expose webmention endpoint in HTTP header, HTML HEAD and HTML BODY.
    """

    def dispatch(self, request, *args, **kwargs):
        obj = MentionableTestModel.objects.get(slug=kwargs.get('slug'))
        html = f'''
            <html>
            <head>
            <link rel="webmention" href="/{constants.namespace}"/></head>
            <body>
            <div>
            {obj.content}
            </div>
            <div>
            <a href="/{constants.namespace}">Webmention endpoint here!</a>
            </div>
            </body>
            </html>
        '''
        response = HttpResponse(html, status=200)
        response['Link'] = mentions.tests.util.snippets.http_header_link(
            constants.webmention_api_absolute_url)
        return response
