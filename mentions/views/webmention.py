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
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View

from mentions.exceptions import TargetDoesNotExist
from mentions.forms.manual_submit_webmention import ManualSubmitWebmentionForm
from mentions.tasks import process_incoming_webmention
from mentions.util import (
    get_mentions_for_url_path,
    serialize_mentions,
    split_url,
)

log = logging.getLogger(__name__)


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def validate(validator, urls):
    for url in urls:
        try:
            validator(url)
        except ValidationError as e:
            log.warning(f'URL \'{url}\' did not pass validation: {e}')
            return False
    return True


# /webmention/
class WebmentionView(View):
    """Handle incoming webmentions."""

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            form = ManualSubmitWebmentionForm()
            return render(request, 'webmention-submit-manual.html', {'form': form})

        log.info('Receiving webmention...')
        http_post = request.POST
        try:
            client_ip = _get_client_ip(request)
            source = http_post['source']
            target = http_post['target']
        except Exception as e:
            log.warning(f'Unable to read webmention params "{http_post}": {e}')
            return HttpResponse(status=400)

        validator = URLValidator(schemes=['http', 'https'])

        if validate(validator, [source, target]):
            log.info(f'Validation passed for source: \'{source}\', target: \'{target}\'')
        else:
            return HttpResponseBadRequest()

        process_incoming_webmention.delay(http_post, client_ip)
        return HttpResponse('Thank you, your webmention has been accepted.', status=202)


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

        scheme, domain, path = split_url(request.build_absolute_uri())
        full_target_url = f'{scheme}://{domain}{for_url}'

        try:
            wm = get_mentions_for_url_path(for_url, full_target_url=full_target_url)
        except TargetDoesNotExist as e:
            log.warning(e)
            return JsonResponse({
                'status': 0,
                'target_url': full_target_url,
                'message': 'Target not found',
            })

        log.info(wm)
        return JsonResponse({
            'status': 1,
            'target_url': full_target_url,
            'mentions': serialize_mentions(wm),
        })
