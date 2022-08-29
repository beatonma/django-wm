from django.db import models

from mentions import permissions as perms

__all__ = [
    "DashboardPermissionProxy",
]


class DashboardPermissionProxy(models.Model):
    """Unmanaged model registers permission required to view mentions dashboard."""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (perms.can_view_dashboard.as_tuple(),)
