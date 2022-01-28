# Mentions

[![Tests](https://github.com/beatonma/django-wm/actions/workflows/runtests.yml/badge.svg)](https://github.com/beatonma/django-wm/actions/workflows/runtests.yml) [![pypi package](https://badge.fury.io/py/django-wm.svg)](https://badge.fury.io/py/django-wm)

`Mentions` lets you add [Webmention](https://indieweb.org/Webmention) functionality to any Django model with minimal setup. Code for an example implementation is available [here](https://github.com/beatonma/django-wm-example).


# Migration warning for existing users

`1.x.x` releases have not included Django migration files, requiring users to run `makemigrations` themselves. This may
result in problems for those users when models defined in `django-wm` change. Version `1.3.1` is the last release affected by this.

Migration files *will* be included from version `2.0.0` onwards, as they should have been from the beginning. Unfortunately
this will require some manual intervention for existing users who need to update. Full instructions for that upgrade will
be provided (thanks to @GriceTurrble).

I apologise to any existing users affected by this change.


# Installation

PyPI: [django-wm](https://pypi.org/project/django-wm/)

```pip install django-wm```


# Setup

### Celery

`Mentions` uses [Celery](https://docs.celeryproject.org/) for running tasks asynchronously. This also requires a [broker](https://docs.celeryproject.org/en/stable/getting-started/backends-and-brokers/index.html) such as [RabbitMQ](https://www.rabbitmq.com).
 
System:

```shell
sudo apt install rabbitmq-server

# Create user for celery service and make sure it can access your database
# e.g:
sudo useradd -N -M --system -s /bin/bash celery
sudo usermod -a -G www-data celery

# Run celery
sudo -u celery env/bin/celery -A projectname worker
```

Project:

> Add `celery.py` to your root project. For an example implementation see [celery.py](https://github.com/beatonma/django-wm-example/blob/master/example/celery.py) from the example project.


# Project code

1. Root project `settings.py`:
   - Set `DOMAIN_NAME`:
   ```python
   DOMAIN_NAME = "your.url.here"  # e.g. "beatonma.org"
   ```

   - Add "mentions" to `INSTALLED_APPS`:
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

    - add `mentions.middleware.WebmentionHeadMiddleware` to `MIDDLEWARE`:
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
       ...

       def all_text(self) -> str:
           return f"{self.introduction} {self.content}"

       def get_absolute_url(self) -> str:
           return reverse("app.views.name", kwargs={"slug": self.slug})
   ```


4. Update migrations:``

    > Warning: If you are updating from version `1.x.x` to `2.0.0` or later, please see [here](#migration-warning-for-existing-users)!
   
   ```shell
   python manage.py makemigrations
   python manage.py migrate
   ```


# Optional Settings

Add these keys to your project `settings.py` to alter default behaviour.

```python
"""
If True, received webmentions are automatically approved and may be publicly visible.
If False, received webmentions require manual approval before they can be made public.
"""
WEBMENTIONS_AUTO_APPROVE = True  # False by default
```
``
