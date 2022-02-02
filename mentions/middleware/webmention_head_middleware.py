from django.conf import settings
from django.urls import reverse

from mentions.views import view_names


class WebmentionHeadMiddleware:
    """Automatically add webmention endpoint to HTTP headers of any HttpResponse
    objects created by this server."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        port = request.META.get("SERVER_PORT", 80)
        path = reverse(view_names.webmention_api_incoming)
        response["Link"] = (
            f"<{request.scheme}://{settings.DOMAIN_NAME}:{port}{path}>"
            ';rel="webmention"'
        )
        return response
