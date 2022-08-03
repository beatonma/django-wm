from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("webmention/", include("mentions.urls")),
    path("", include("sample_app.urls")),
]
