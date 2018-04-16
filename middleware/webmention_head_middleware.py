from django.conf import settings


class WebmentionHeadMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # response['Link'] = '<https://beatonma.org/webmention>;rel="webmention"'
        response['Link'] = (
            '<{}/webmention>;rel="webmention"'
            .format(settings.DOMAIN_NAME))
        return response
