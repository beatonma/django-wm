import logging
from typing import Optional

from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View

from mentions.forms import SubmitWebmentionForm
from mentions.tasks import handle_incoming_webmention

__all__ = [
    "WebmentionView",
]

log = logging.getLogger(__name__)


# /webmention/
class WebmentionView(View):
    """Handle incoming webmentions."""

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = SubmitWebmentionForm()
        return render(
            request,
            "mentions/webmention-submit-manual.html",
            {
                "form": form,
            },
        )

    def post(self, request):
        log.debug("Receiving webmention...")
        form = SubmitWebmentionForm(request.POST)

        if not form.is_valid():
            log.info(f"Received webmention failed form validation: {form.data}")
            return HttpResponseBadRequest()

        data = form.cleaned_data
        source = data["source"]
        target = data["target"]
        client_ip = _get_client_ip(request)

        log.info(
            f"Accepted webmention submission (not yet verified): {source} -> {target}"
        )

        handle_incoming_webmention(source=source, target=target, sent_by=client_ip)
        return render(request, "mentions/webmention-accepted.html", status=202)


def _get_client_ip(request) -> Optional[str]:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[-1].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
