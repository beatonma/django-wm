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


class MockResponse:
    """Mock of requests.Response."""

    def __init__(
        self,
        url: str,
        headers: dict = None,
        text: str = None,
        status_code: int = None,
    ):
        self.url = url
        self.text = text
        self.status_code = status_code
        self.headers = headers
