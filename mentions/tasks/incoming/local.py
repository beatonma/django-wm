from typing import Optional

from django.conf import settings

from mentions.exceptions import BadConfig, TargetWrongDomain
from mentions.resolution import get_model_for_url_path
from mentions.util import split_url

__all__ = [
    "get_target_object",
]


def get_target_object(target_url: str) -> Optional["MentionableMixin"]:
    """Confirm that the page exists on our server and return object.

    Args:
        target_url: Our URL that is being mentioned.

    Raises:
        TargetWrongDomain: If the target_url points to a domain not listed in settings.ALLOWED_HOSTS
        BadConfig: Raised from get_model_for_url_path
    """
    scheme, domain, path = split_url(target_url)

    if domain not in settings.ALLOWED_HOSTS:
        raise TargetWrongDomain(f"Wrong domain: {domain} (from url={target_url})")

    try:
        return get_model_for_url_path(path)

    except BadConfig:
        # target_url is not configured to resolve to a model instance.
        pass
