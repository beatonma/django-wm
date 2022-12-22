import logging

from django.views import View

from mentions import options

log = logging.getLogger(__name__)

default_context = {
    "DOMAIN_NAME": options.domain_name(),
}


class BaseView(View):
    def dispatch(self, request, *args, **kwargs):
        log.info(f"{request} | {request.headers}")
        return super().dispatch(request, *args, **kwargs)
