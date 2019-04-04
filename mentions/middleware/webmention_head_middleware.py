from django.conf import settings


class WebmentionHeadMiddleware:
    """Automatically add webmention endpoint to HTTP headers of any HttpResponse
    objects created by this server."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Link'] = (
            f'<{settings.DOMAIN_NAME}/{settings.WEBMENTION_NAMESPACE}>'
            ';rel="webmention"')
        return response
