from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("webmention/", include("mentions.urls")),
]

try:
    from wagtail import urls as wagtail_urls
    from wagtail.admin import urls as wagtailadmin_urls

except ImportError:
    wagtail_urls = None

if wagtail_urls is not None:
    urlpatterns += [
        path("vanilla/", include("sample_app.urls")),
        path("admin/", include(wagtailadmin_urls)),
        path("", include("sample_app_wagtail.urls")),
        path("", include(wagtail_urls)),
    ]

else:
    urlpatterns += [
        path("", include("sample_app.urls")),
    ]
