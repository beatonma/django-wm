from typing import cast

from django.db.models import QuerySet


class WebmentionQuerySet(QuerySet):
    def filter(self, *args, **kwargs) -> "WebmentionQuerySet":
        return cast(WebmentionQuerySet, super().filter(*args, **kwargs))

    def filter_unread(self) -> "WebmentionQuerySet":
        return self.filter(has_been_read=False)

    def filter_approved(self) -> "WebmentionQuerySet":
        return self.filter(approved=True)

    def filter_validated(self) -> "WebmentionQuerySet":
        return self.filter(validated=True)

    def filter_public(self) -> "WebmentionQuerySet":
        return self.filter_approved().filter_validated()

    def mark_as_approved(self) -> int:
        return self.update(approved=True)

    def mark_as_unapproved(self) -> int:
        return self.update(approved=False)

    def mark_as_read(self) -> int:
        return self.update(has_been_read=True)

    def mark_as_unread(self) -> int:
        return self.update(has_been_read=False)
