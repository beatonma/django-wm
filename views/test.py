from django.http import HttpResponse
from django.views.generic.base import View


class MentionableTestStubView(View):
    '''
    Stub view for testing.
    '''

    def dispatch(self, request, *args, **kwargs):
        return HttpResponse(status=200)
