"""Modules should import wagtail components from here.

The library should work with (and without)wWagtail==3.0.3 and above. The @path
decorator was only introduced in wagtail==4.0.0 so we need to handle it being
unavailable."""

from mentions.exceptions import OptionalDependency

try:
    from wagtail.contrib.routable_page.models import RoutablePageMixin
    from wagtail.contrib.routable_page.models import path as wagtail_path
    from wagtail.contrib.routable_page.models import re_path as wagtail_re_path

except ImportError:

    def config_error(function_name: str, min_wagtail_version: str, django_func):
        """When wagtail is not available or"""

        def fake_decorator(pattern, name):
            def raise_error(*args, **kwargs):
                raise OptionalDependency(
                    f"Tried to use decorator '{function_name}' but "
                    f"wagtail>={min_wagtail_version} is not installed. ("
                    f"pattern={pattern}, name={name})"
                )

            def fake_wrapper(view_func):
                if not hasattr(view_func, "_routablepage_routes"):
                    view_func._routablepage_routes = []

                view_func._routablepage_routes.append(
                    (
                        django_func(
                            pattern,
                            raise_error,
                            name=name or view_func.__name__,
                        ),
                        1000,
                    )
                )
                return view_func

            return fake_wrapper

        return fake_decorator

    try:
        from django.urls import re_path
        from wagtail.contrib.routable_page.models import RoutablePageMixin
        from wagtail.contrib.routable_page.models import route as wagtail_re_path

    except ImportError:
        wagtail_re_path = config_error("mentions_wagtail_re_path", "3.0.3", re_path)

        class RoutablePageMixin:
            pass

    from django.urls import path

    wagtail_path = config_error("mentions_wagtail_path", "4.0", path)
