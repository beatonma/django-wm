from importlib.util import find_spec

from .default_settings import *

is_wagtail_installed = find_spec("wagtail") is not None
if is_wagtail_installed:
    from .wagtail_settings import INSTALLED_APPS as WAGTAIL_APPS

    INSTALLED_APPS += WAGTAIL_APPS
