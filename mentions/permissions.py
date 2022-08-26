from dataclasses import dataclass
from typing import Tuple

from mentions.apps import MentionsConfig

__all__ = [
    "can_approve_webmention",
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

    def fqn(self) -> str:
        return f"{MentionsConfig.name}.{self.codename}"


can_approve_webmention = MentionsPermission(
    "approve_webmention",
    "Can approve received Webmentions for publishing.",
)
can_view_dashboard = MentionsPermission(
    "view_webmention_dashboard",
    "Can view the webmention dashboard/status page.",
)
