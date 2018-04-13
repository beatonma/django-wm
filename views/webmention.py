import logging

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import (
    HttpResponse,
    JsonResponse,
    HttpResponseBadRequest,     # HTTP 400
    HttpResponseNotAllowed,     # HTTP 405
)
from django.shortcuts import render
from django.views.generic.base import View

from mentions.tasks import process_incoming_webmention

from main.models import App, Article, Changelog


log = logging.getLogger(__name__)

# Classes that use the WebMentionableMixin
MENTIONABLE_MODELS = [
    App,
    Article,
    Changelog,
]


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class WebmentionView(View):
    """Handle incoming webmentions."""

    def dispatch(self, request, *args, **kwargs):
        if request.method != 'POST':
            return HttpResponseNotAllowed(
                ['POST', ],
                'Only POST requests are accepted')

        try:
            http_post = request.POST
            client_ip = _get_client_ip(request)
            source = http_post['source']
            target = http_post['target']
        except Exception as e:
            log.warn(
                'Unable to read webmention params "{}": {}'
                .format(http_post, e))

        validate = URLValidator(schemes=['http', 'https'])

        try:
            validate(source)
            validate(target)
        except ValidationError as e:
            log.warn('URL did not pass validation: {}'.format(e))
            return HttpResponseBadRequest()

        process_incoming_webmention.delay(http_post, client_ip)
        return HttpResponse(status=202)


class GetWebmentionsView(View):
    """Return any webmentions associated with a given item."""

    def dispatch(self, request, *args, **kwargs):
        if request.method != 'GET':
            return HttpResponseNotAllowed(['GET', ])

        try:
            # model_name = request.GET['for']
            # slug = request.GET['id']
            url = request.GET['url']
        except Exception as e:
            log.warn(
                'Unable to read params for GetWebmentionsView(): {}'
                .format(e))
            return HttpResponseBadRequest()
        # TODO
        # webmentions.objects.filter(target=url)
        # 
        # for m in MENTIONABLE_MODELS:
        #     if m._meta.verbose_name.lower() == model_name:
                # m.objects.filter(slug=slug)
                

        return HttpResponse(status=500)
