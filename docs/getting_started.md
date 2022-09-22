# Installation

PyPI: [django-wm](https://pypi.org/project/django-wm/)

### With `celery` (recommended)
```pip install django-wm[celery]```

Please follow [these instructions](getting_started_with_celery.md) to set up Celery, then come back here for the rest.

### Without `celery`:
```pip install django-wm```

Please follow [these instructions](getting_started_without_celery.md), then come back here for the rest.


### Project code

For reference, source code for an example project is available [here](https://github.com/beatonma/django-wm-example).

1. Root project `settings.py`:
   - Set `DOMAIN_NAME`:
   ```python
   DOMAIN_NAME = "your.url.here"  # e.g. "beatonma.org"
   ```

   - Add `mentions` to `INSTALLED_APPS`:
    ```python
    INSTALLED_APPS = [
        "django.contrib.auth",
        "django.contrib.contenttypes",
        ...
        "mentions",
    ]
    ```

    - Add `mentions.middleware.WebmentionHeadMiddleware` to `MIDDLEWARE`:
    ```python
    MIDDLEWARE = [
        ...
        "mentions.middleware.WebmentionHeadMiddleware",
    ]
    ```


2. Root project `urls.py`:
    ```python
    urlpatterns = [
        ...
        path("webmentions/", include("mentions.urls")),
    ]
   ```


3. Include `MentionableMixin` in the model(s) you want to support webmention functionality.

   **IMPORTANT**: Any models that include the mixin must also implement `all_text` and `get_absolute_url` methods:

   ```python
   from mentions.models.mixins.mentionable import MentionableMixin

   class MyModel(MentionableMixin, models.Model):

       def all_text(self) -> str:
           return f"{self.introduction} {self.content}"

       def get_absolute_url(self) -> str:
           return reverse("my-model-view-name", args=[self.slug])
   ```


4. `urlpatterns` keywords.

   Any `urlpatterns` `path` or `re_path` entries that represent a `MentionableMixin` model need to provide `slug` and `model_name` kwargs. The `slug` should be defined within the pattern for the path, whereas `model_name` needs to added to the `kwargs` argument.
   
   ```djangourlpath
   urlpatterns =  [
      path(
         "articles/<slug:slug>/",  # `slug` provided as part of the path pattern
         MyMentionableView.as_view(),
         kwargs={
            "model_name": "my_app.MyMentionableModel"  # `model_name` must be provided explicitly
         }
         name="my-model-view-name"
      )
   ]
   ```


5. Update migrations:

    > **Warning**: If you are updating from version `1.x.x` to `2.0.0` or later, please see [here](#migration-warning-for-existing-users)!
   
   ```shell
   python manage.py makemigrations
   python manage.py migrate
   ```
   
6. Test it! [This page](https://beatonma.org/webmentions_tester/) accepts Webmentions and lets you send one to yourself, so you can check that both incoming and outgoing Webmentions work on your server.


# Optional Settings

```python
# settings.py

"""
If `True`, received webmentions are automatically approved and may be publicly visible.
If `False`, received webmentions require manual approval before they can be made public.
"""
WEBMENTIONS_AUTO_APPROVE: bool = False

"""Specifies the time (in seconds) to wait for network calls to resolve."""
WEBMENTIONS_TIMEOUT: float = 10

"""Specifies the minimum time (in seconds) to wait before retrying to process a webmention."""
WEBMENTIONS_RETRY_INTERVAL: int = 600

"""Specifies how many times we can attempt to process a mention before giving up."""
WEBMENTIONS_MAX_RETRIES: int = 5

"""
Specifies whether the the `dashboard/` view can be viewed by anyone.
If `False` (default), the `dashboard/` view is only available to users with
`mentions.view_webmention_dashboard` permission.
"""
WEBMENTIONS_DASHBOARD_PUBLIC: bool = False
```
