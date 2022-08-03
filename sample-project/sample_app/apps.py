import sys

from django.apps import AppConfig
from django.conf import settings


class SampleAppConfig(AppConfig):
    name = "sample_app"

    def ready(self):
        if "runserver" not in sys.argv:
            # Don't create default article when running tests or migrations.
            return

        from sample_app.models import Article

        Article.objects.get_or_create(
            # pk=1,
            title=f"First article on {settings.DOMAIN_NAME}",
            defaults={
                "content": "Something to talk about",
                "author": "A. Mouse",
                "allow_incoming_webmentions": True,
            },
        )
