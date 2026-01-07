from django.db import models

from mentions import config


def URLField(verbose_name=None, name=None, **kwargs):
    """Proxy for models.URLField, allowing for app-wide default configuration."""
    kwargs.setdefault("max_length", config.MAX_URL_LENGTH)
    return models.URLField(verbose_name, name, **kwargs)
