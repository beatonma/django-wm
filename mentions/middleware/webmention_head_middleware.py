from django.urls import reverse

from mentions import config
from mentions.views import view_names

__all__ = [
    "WebmentionHeadMiddleware",
]


class WebmentionHeadMiddleware:
    """Automatically add webmention endpoint to HTTP headers of any HttpResponse
    objects created by this server."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        path = reverse(view_names.webmention_api_incoming)

        existing = response.get("Link")
        endpoint_link = f'<{config.build_url(path)}>; rel="webmention"'

        response["Link"] = ",".join([x for x in [existing, endpoint_link] if x])

        return response
