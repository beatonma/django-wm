from django.db import models

from mentions.models.base import MentionsBaseModel

__all__ = [
    "HCard",
]


class HCard(MentionsBaseModel):
    """An h-card represents information about a person or organisation.

    Spec: https://microformats.org/wiki/h-card
    """

    name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Name of the person/organisation",
    )
    avatar = models.URLField(
        blank=True,
        null=True,
        help_text="Link to their profile image",
    )
    homepage = models.URLField(
        blank=True,
        null=True,
        help_text="Link to their homepage",
    )
    json = models.TextField(
        blank=True,
        help_text="Raw json representation of this hcard",
    )

    def __str__(self):
        return f'HCard(name="{self.name}", avatar="{self.avatar}", homepage="{self.homepage})"'
