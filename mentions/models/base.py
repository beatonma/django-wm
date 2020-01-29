"""

"""

import logging

from django.db import models

log = logging.getLogger(__name__)


class MentionsBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        abstract = True
