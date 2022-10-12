import logging

from django.http import HttpResponseBadRequest, JsonResponse
from django.views import View

from mentions import config
from mentions.exceptions import TargetDoesNotExist
from mentions.resolution import get_mentions_for_url
from mentions.serialize import serialize_mentions

__all__ = [
    "GetMentionsView",
]

log = logging.getLogger(__name__)


# /webmention/get
class GetMentionsView(View):
    """Return any mentions (Webmention, SimpleMention) associated with a given url."""

    def get(self, request):
        for_urlpath = request.GET.get("url")

        if not for_urlpath:
            return HttpResponseBadRequest("Missing args")

        full_target_url = config.build_url(for_urlpath)

        try:
            wm = get_mentions_for_url(full_target_url)

            return JsonResponse(
                {
                    "target_url": full_target_url,
                    "mentions": serialize_mentions(wm),
                }
            )

        except TargetDoesNotExist as e:
            log.warning(e)
            return JsonResponse(
                {
                    "target_url": full_target_url,
                    "message": "Target not found",
                    "mentions": [],
                },
                status=404,
            )
