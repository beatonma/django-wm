from mentions import contract, permissions
from mentions.models import Webmention


def unread_webmentions(request) -> dict:
    if not permissions.can_change_webmention.has_perm(request.user):
        return {}

    return {
        contract.CONTEXT_UNREAD_WEBMENTIONS: Webmention.objects.filter_unread(),
    }
