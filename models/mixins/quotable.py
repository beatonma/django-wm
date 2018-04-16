import logging

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from mentions.models.hcard import HCard

log = logging.getLogger()


class QuotableMixin(models.Model):
    class Meta:
        abstract = True

    target_url = models.URLField(
        help_text='Our URL that is mentioned')
    source_url = models.URLField(
        help_text='The URL that mentions our content')

    quote = models.CharField(
        max_length=300,
        help_text='A short excerpt from the quoted piece')

    published = models.DateTimeField(auto_now_add=True)

    hcard = models.ForeignKey(
        HCard,
        blank=True,
        null=True,
        on_delete=models.CASCADE)

    # The mention target may be an instance of any class that
    # uses the QuotableMixin so we need to use a GenericForeignKey
    content_type = models.ForeignKey(
        ContentType,
        null=True,
        on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target_object = GenericForeignKey('content_type', 'object_id')
