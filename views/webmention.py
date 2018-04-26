import logging

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import (
    HttpResponse,
    JsonResponse,
    HttpResponseBadRequest,     # HTTP 400
    HttpResponseNotAllowed,     # HTTP 405
)
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View

from mentions.exceptions import BadConfig, TargetDoesNotExist
from mentions.tasks import process_incoming_webmention
from mentions.util import get_model_for_url


log = logging.getLogger(__name__)


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# /webmention
class WebmentionView(View):
    """Handle incoming webmentions."""

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        log.info('Receiving webmention...')
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
            return HttpResponse(status=400)

        validate = URLValidator(schemes=['http', 'https'])

        try:
            validate(source)
            validate(target)
            log.info('Both urls are valid')
        except ValidationError as e:
            log.warn('URL did not pass validation: {}'.format(e))
            return HttpResponseBadRequest()

        process_incoming_webmention.delay(http_post, client_ip)
        return HttpResponse(status=202)


# /webmention/get
class GetWebmentionsView(View):
    """Return any webmentions associated with a given item."""

    def dispatch(self, request, *args, **kwargs):
        if request.method != 'GET':
            return HttpResponseNotAllowed(['GET', ])

        http_get = request.GET
        for_url = http_get.get('url')

        if not for_url:
            return HttpResponseBadRequest('Missing args')

        try:
            obj = get_model_for_url(for_url)
        except TargetDoesNotExist as e:
            log.info(e)
            return JsonResponse({
                'status': 0,
                'message': 'Target object not found'
            })
        except BadConfig as e:
            log.error(e)
            return JsonResponse({
                'status': 0,
                'message': 'Config error'
            })

        wm = obj.mentions
        log.info(wm)
        return JsonResponse({
            'mentions': obj.mentions_json(),
        })
