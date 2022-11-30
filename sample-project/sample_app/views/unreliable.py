import logging
import random
import time

from django.http import HttpResponse
from sample_app.views import BaseView

from mentions import options

log = logging.getLogger(__name__)


class TimeoutView(BaseView):
    """A view which takes too long to respond."""

    def get(self, request):
        time.sleep(options.timeout() + 1)
        return HttpResponse("That took a while!", status=200)


class MaybeTimeoutView(BaseView):
    def get(self, request):
        timed_out = random.random() > 0.4

        if timed_out:
            log.info("MaybeTimeoutView timed out!")
            time.sleep(options.timeout() + 1)

        return HttpResponse(f"timed_out={timed_out}", status=200)
