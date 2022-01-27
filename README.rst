Mentions
========
.. image:: https://badge.fury.io/py/django-wm.svg
    :target: https://badge.fury.io/py/django-wm

Mentions lets you add Webmention_ functionality to any Django model with minimal
setup. Code for an example implementation is available  here_.

.. _webmention: https://indieweb.org/Webmention
.. _here: https://github.com/beatonma/django-wm-example


Migration warning for existing users
====================================
`1.x.x` releases have not included Django migration files, requiring users to run `makemigrations` themselves. This may
result in problems for those users when models defined in `django-wm` change. `1.3.1` is the last release affected by this.

Migration files *will* be included from version `2.0.0` onwards, as they should have been from the beginning. Unfortunately
this will require some manual intervention for existing users who need to update. Full instructions for that upgrade will
be provided (thanks to @GriceTurrble).

I apologise to any existing users affected by this change.


Installation
============

PyPI: django-wm_

:code:`pip install django-wm`

.. _django-wm: https://pypi.org/project/django-wm/


Setup
=====

Celery
------
Mentions uses Celery_ and RabbitMQ_ for running tasks asynchronously.
If you do not use them already you will need to set them up first.

.. _Celery: http://www.celeryproject.org
.. _RabbitMQ: https://www.rabbitmq.com


System::

    sudo apt install rabbitmq-server

    # Create user for celery service and make sure it can access your database
    # e.g:
    sudo useradd -N -M --system -s /bin/bash celery
    sudo usermod -a -G www-data celery

    # Run celery
    sudo -u celery env/bin/celery -A projectname worker &


Project:

    Add :code:`celery.py` to your root project. For an example implementation
    see celery.py_ from the example project.

.. _celery.py: https://github.com/beatonma/django-wm-example/blob/master/example/celery.py


Project code
------------

1. Root project :code:`settings.py`:

    * Set :code:`DOMAIN_NAME`::

        DOMAIN_NAME = "your.url.here"  # e.g. "beatonma.org"

    * Add "mentions" to :code:`INSTALLED_APPS`::

        INSTALLED_APPS = [
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.flatpages',
            'django.contrib.sites',
            ...
            'mentions',
        ]

    * Add :code:'mentions.middleware.WebmentionHeadMiddleware' to :code:`MIDDLEWARE`::

        MIDDLEWARE = [
            ...
            'mentions.middleware.WebmentionHeadMiddleware',
        ]


2. Root project :code:`urls.py` ::

    urlpatterns = [
        ...
        path('webmentions/', include('mentions.urls')),
    ]


3. Include :code:`MentionableMixin` in the model(s) you want to support
   webmention functionality.

   IMPORTANT: Any models that include the mixin must also
   implement :code:`all_text` and :code:`get_absolute_url` methods::

    from mentions.models.mixins.mentionable import MentionableMixin
    ...

    class MyModel(MentionableMixin, models.Model):
        ...
        def all_text(self) -> str:
            return f'{self.introduction} {self.content}'

        def get_absolute_url() -> str:
            return reverse('app.views.name', kwargs={'slug': self.slug})


4. Update database tables::

    python manage.py makemigrations
    python manage.py migrate




Optional Settings
-----------------

Add these keys to your project :code:`settings.py` to alter default behaviour.

    :code:`WEBMENTIONS_AUTO_APPROVE` = :code:`bool` (default: :code:`False`)

    * :code:`True`: Received webmentions are automatically approved and may be publicly visible.
    * :code:`False`: Received webmentions require manual approval before they can be made public.
