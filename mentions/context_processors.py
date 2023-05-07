from mentions import contract
from mentions.models import Webmention


def unread_webmentions(request) -> dict:
    if not request.user.has_perm("mentions.change_webmention"):
        return {}

    return {
        contract.CONTEXT_UNREAD_WEBMENTIONS: Webmention.objects.filter_unread(),
    }
