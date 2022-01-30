import logging
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

log = logging.getLogger(__name__)

SETTINGS = "mentions.tests.config.test_settings"


if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = SETTINGS

    django.setup()

    # Update value of constants.webmention_api_absolute_url after django setup is complete
    # so we can build strings with resolved reverse_lazy.
    import mentions.tests.util.constants as constants

    constants.webmention_api_absolute_url = (
        f"https://{constants.domain}{constants.webmention_api_relative_url}"
    )

    test_runner = get_runner(settings)()
    failures = test_runner.run_tests(["mentions.tests"])

    sys.exit(bool(failures))
