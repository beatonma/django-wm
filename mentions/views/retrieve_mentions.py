import logging

from django.http import HttpResponseBadRequest, JsonResponse
from django.views import View

from mentions.exceptions import TargetDoesNotExist
from mentions.resolution import get_mentions_for_url_path
from mentions.serialize import serialize_mentions
from mentions.util import split_url

log = logging.getLogger(__name__)


# /webmention/get
class GetMentionsView(View):
    """Return any mentions (Webmention, SimpleMention) associated with a given url."""

    def get(self, request):
        for_url = request.GET.get("url")

        if not for_url:
            return HttpResponseBadRequest("Missing args")

        scheme, domain, path = split_url(request.build_absolute_uri())
        full_target_url = f"{scheme}://{domain}{for_url}"

        try:
            wm = get_mentions_for_url_path(for_url, full_target_url=full_target_url)

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
