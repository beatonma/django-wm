from __future__ import absolute_import, unicode_literals

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sample_project.settings")

try:
    from celery import Celery

    app = Celery("sample_project")
    app.config_from_object("django.conf:settings", namespace="CELERY")
    app.autodiscover_tasks()

except ImportError:
    app = None
