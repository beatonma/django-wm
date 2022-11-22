from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = [
    "MentionsBaseModel",
]


class MentionsBaseModel(models.Model):
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, null=True)

    class Meta:
        abstract = True
