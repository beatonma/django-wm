import logging

from django.core.exceptions import BadRequest
from django.http import JsonResponse
from django.views import View

from mentions import config
from mentions.exceptions import TargetDoesNotExist
from mentions.resolution import get_mentions_for_url
from mentions.views import contract
from mentions.views.serialize import serialize_mentions, serialize_mentions_by_type

__all__ = [
    "GetMentionsView",
    "GetMentionsByTypeView",
]

log = logging.getLogger(__name__)


def build_url(request) -> str:
    for_urlpath = request.GET.get("url")

    if not for_urlpath:
        raise BadRequest()

    return config.build_url(for_urlpath)


# /webmention/get
class GetMentionsView(View):
    def get(self, request):
        """Return any mentions associated with a given url."""
        full_target_url = build_url(request)

        try:
            mentions = get_mentions_for_url(full_target_url)

            return JsonResponse(
                {
                    contract.TARGET_URL: full_target_url,
                    contract.MENTIONS: serialize_mentions(mentions),
                }
            )

        except TargetDoesNotExist as e:
            log.warning(e)
            return JsonResponse(
                {
                    contract.TARGET_URL: full_target_url,
                    contract.MESSAGE: "Target not found",
                    contract.MENTIONS: [],
                },
                status=404,
            )


# /webmention/get_by_type
class GetMentionsByTypeView(View):
    def get(self, request):
        """Return any mentions associated with a given url, grouped by type."""
        full_target_url = build_url(request)

        try:
            mentions = get_mentions_for_url(full_target_url)

            return JsonResponse(
                {
                    contract.TARGET_URL: full_target_url,
                    contract.MENTIONS_BY_TYPE: serialize_mentions_by_type(mentions),
                }
            )

        except TargetDoesNotExist as e:
            log.warning(e)
            return JsonResponse(
                {
                    contract.TARGET_URL: full_target_url,
                    contract.MESSAGE: "Target not found",
                    contract.MENTIONS_BY_TYPE: serialize_mentions_by_type([]),
                },
                status=404,
            )
