from typing import Optional, Type

from django.db import models
from django.utils.translation import gettext_lazy as _

from mentions.models.base import MentionsBaseModel

__all__ = [
    "HCard",
    "update_or_create_hcard",
]


class HCard(MentionsBaseModel):
    """An h-card represents information about a person or organisation.

    Spec: https://microformats.org/wiki/h-card
    """

    name = models.CharField(
        _("name"),
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Name of the person/organisation."),
    )
    avatar = models.URLField(
        _("avatar URL"),
        blank=True,
        null=True,
        help_text=_("Link to their profile image."),
    )
    homepage = models.URLField(
        _("homepage URL"),
        blank=True,
        null=True,
        help_text=_("Link to their homepage."),
    )
    json = models.TextField(
        _("JSON"),
        blank=True,
        help_text=_("Raw json representation of this h-card."),
    )

    def __str__(self):
        return f'HCard(name="{self.name}", avatar="{self.avatar}", homepage="{self.homepage})"'

    class Meta:
        verbose_name = _("h-card")
        verbose_name_plural = _("h-cards")


def update_or_create_hcard(
    homepage: Optional[str],
    name: Optional[str],
    avatar: Optional[str],
    data: str,
) -> HCard:
    """Any individual field may be used to create/retrieve an HCard.

    Ideally, homepage and name are used together.

    Otherwise, the order of precedence is [homepage, name, avatar].
    """

    if homepage and name:
        return _update_first_or_create(
            HCard,
            homepage=homepage,
            name=name,
            defaults={
                "avatar": avatar,
                "json": data,
            },
        )

    if homepage:
        return _update_first_or_create(
            HCard,
            homepage=homepage,
            name=None,
            defaults={
                "avatar": avatar,
                "json": data,
            },
        )

    if name:
        return _update_first_or_create(
            HCard,
            homepage=None,
            name=name,
            defaults={
                "avatar": avatar,
                "json": data,
            },
        )

    if avatar:
        return _update_first_or_create(
            HCard,
            homepage=None,
            name=None,
            avatar=avatar,
            defaults={
                "json": data,
            },
        )


def _update_first_or_create(
    model_cls: Type[MentionsBaseModel],
    defaults: dict,
    **query,
):
    try:
        return model_cls.objects.update_or_create(
            **query,
            defaults=defaults,
        )[0]

    except model_cls.MultipleObjectsReturned:
        instance = model_cls.objects.filter(**query).first()
        for key, value in defaults.items():
            setattr(instance, key, value)

        instance.save()
        return instance
