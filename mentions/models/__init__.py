from django.db import models


class MentionsBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        abstract = True


from .hcard import *
from .manual_mention import *
from .pending import *
from .webmention import *
