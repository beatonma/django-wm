# Upgrading

**Version `2.0` has potentially BREAKING CHANGES for any users upgrading from `1.x.x`!** If you used any `1.x.x` version of `django-wm` please follow [these instructions](upgrading_to_2.0.md) to upgrade to `2.0.1` without data loss. Please complete the upgrade to `2.0.1` before upgrading further to any later versions.


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
        "django.contrib.flatpages",
        "django.contrib.sites",
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

Add these keys to your project `settings.py` to alter default behaviour.

```python
"""
If True, received webmentions are automatically approved and may be publicly visible.
If False, received webmentions require manual approval before they can be made public.
"""
WEBMENTIONS_AUTO_APPROVE = True  # False by default
```
