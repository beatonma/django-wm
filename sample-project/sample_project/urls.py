from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("webmention/", include("mentions.urls")),
    path("issues/", include("issues_app.urls")),
]


try:
    from wagtail import urls as wagtail_urls
    from wagtail.admin import urls as wagtailadmin_urls

    urlpatterns += [
        path("vanilla/", include("sample_app.urls")),
        path("admin/", include(wagtailadmin_urls)),
        path("", include("sample_app_wagtail.urls")),
        path("", include(wagtail_urls)),
    ]

except ImportError:
    urlpatterns += [
        path("", include("sample_app.urls")),
    ]

urlpatterns += staticfiles_urlpatterns()
