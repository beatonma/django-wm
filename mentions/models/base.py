from django.db import models

__all__ = [
    "MentionsBaseModel",
]


class MentionsBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        abstract = True
