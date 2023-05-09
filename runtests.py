#!env/bin/python
import logging
import os
import sys
from argparse import ArgumentParser

import django
from django.conf import settings
from django.core.management import execute_from_command_line
from django.test.utils import get_runner

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)

SETTINGS_PATH = "tests.config.settings"

APPS = {
    "test_app": {
        "EXTRA_APPS": [],
    },
    "test_wagtail_app": {
        "EXTRA_APPS": [
            "wagtail.users",
            "wagtail",
        ]
    },
}


def parse_clargs():
    parser = ArgumentParser()

    parser.add_argument(
        "--makemigrations",
        nargs=1,
        help="Run makemigrations for the given test-specific app.",
    )

    parser.add_argument("--path", type=str, default="tests")

    parsed, remaining_ = parser.parse_known_args()

    if parsed.makemigrations:
        parsed.app_name = parsed.makemigrations[0]

    return parsed, remaining_


def _make_migrations(app_name: str):
    extra_apps = APPS[app_name]["EXTRA_APPS"]
    migrations_settings = {
        "DEBUG": False,
        "SECRET_KEY": "django-wm-fake-key",
        "INSTALLED_APPS": [
            "django.contrib.auth",
            "django.contrib.contenttypes",
            *extra_apps,
            f"tests.{app_name}",
            "mentions",
        ],
        "DEFAULT_AUTO_FIELD": "django.db.models.BigAutoField",
    }

    settings.configure(**migrations_settings)
    django.setup()

    args = sys.argv + ["makemigrations", app_name]
    execute_from_command_line(args)

    sys.exit()


def _runtests(path: str):
    def get_sys_args() -> list:
        args_ = sys.argv
        position = None
        for index, x in enumerate(args_):
            if x.endswith("runtests.py"):
                position = index + 1
                break

        return args_[position:]

    os.environ["DJANGO_SETTINGS_MODULE"] = SETTINGS_PATH

    django.setup()

    log.info(get_version_info())

    test_runner = get_runner(settings)()

    # Detailed report for any tests that are non-passing (failed, skipped...)
    default_args = "-r a".split(" ")
    args = get_sys_args() or default_args

    failures = test_runner.run_tests([path, *args])

    sys.exit(bool(failures))


def get_version_info():
    import mentions

    try:
        import wagtail
    except ImportError:
        wagtail = lambda: 1
        setattr(wagtail, "__version__", "not-installed")
    return (
        f"mentions=={mentions.__version__}, "
        f"django=={django.__version__}, "
        f"wagtail=={getattr(wagtail, '__version__')}"
    )


if __name__ == "__main__":
    keep_clargs = sys.argv[0:1]  # Save the script name.
    clargs, remaining = parse_clargs()
    sys.argv = keep_clargs + remaining

    if clargs.makemigrations:
        _make_migrations(clargs.app_name)
    else:
        _runtests(clargs.path)
