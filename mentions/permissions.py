from dataclasses import dataclass
from typing import Tuple

from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _

from mentions.apps import MentionsConfig

__all__ = [
    "can_change_webmention",
    "can_view_dashboard",
]


@dataclass
class MentionsPermission:
    codename: str
    description: str

    def as_tuple(self) -> Tuple[str, str]:
        return self.codename, self.description

    def has_perm(self, user, obj=None) -> bool:
        return user.has_perm(self.fqn(), obj=obj)

    def grant(self, user):
        user.user_permissions.add(self.get_from_db())

    def fqn(self) -> str:
        return f"{MentionsConfig.name}.{self.codename}"

    def get_from_db(self):
        return Permission.objects.get(codename=self.codename)

    def __str__(self):
        return self.fqn()


can_view_dashboard = MentionsPermission(
    "view_webmention_dashboard",
    _("Can view the webmention dashboard/status page."),
)


# The following permissions are created automatically by Django.
can_change_webmention = MentionsPermission(
    "change_webmention", _("Default 'change' permission for Webmention model.")
)
