from django.urls import path
from sample_app_wagtail.views import ActionView

urlpatterns = [
    path("", ActionView.as_view(), name="wagtail-actions"),
]
