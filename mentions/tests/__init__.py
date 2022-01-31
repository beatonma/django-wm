from django.test import TestCase


class WebmentionTestCase(TestCase):
    def tearDown(self) -> None:
        super().tearDown()
        from mentions.models import (
            HCard,
            OutgoingWebmentionStatus,
            SimpleMention,
            Webmention,
        )

        for Model in [
            Webmention,
            OutgoingWebmentionStatus,
            HCard,
            SimpleMention,
        ]:
            Model.objects.all().delete()
