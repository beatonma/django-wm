import logging

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View

from mentions.forms.manual_submit_webmention import ManualSubmitWebmentionForm
from mentions.tasks.scheduling import handle_incoming_webmention

log = logging.getLogger(__name__)


# /webmention/
class WebmentionView(View):
    """Handle incoming webmentions."""

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = ManualSubmitWebmentionForm()
        return render(request, "webmention-submit-manual.html", {"form": form})

    def post(self, request):
        log.info("Receiving webmention...")
        http_post = request.POST

        try:
            client_ip = _get_client_ip(request)
            source = http_post["source"]
            target = http_post["target"]

        except Exception as e:
            log.warning(f"Unable to read webmention params '{http_post}': {e}")
            return HttpResponseBadRequest()

        validator = URLValidator(schemes=["http", "https"])

        if _validate(validator, [source, target]):
            log.info(f"Validation passed for source: '{source}', target: '{target}'")
        else:
            return HttpResponseBadRequest()

        handle_incoming_webmention(http_post, client_ip)
        return HttpResponse("Thank you, your webmention has been accepted.", status=202)


def _get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[-1].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def _validate(validator, urls):
    for url in urls:
        try:
            validator(url)
        except ValidationError as e:
            log.warning(f"URL '{url}' did not pass validation: {e}")
            return False
    return True
