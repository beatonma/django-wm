Mentions
========

Mentions lets you add Webmention_ functionality to any Django model with minimal
setup. There is an implementation running at https://django-wm.dev/ with source
code available here_.

.. _webmention: https://indieweb.org/Webmention
.. _here: https://github.com/beatonma/django-wm-example


Installation
============
:code:`pip install django-wm`


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

    * Add "mentions" to INSTALLED_APPS::

        INSTALLED_APPS = [
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.flatpages',
            'django.contrib.sites',
            ...
            'mentions',
        ]

    * Add 'mentions.middleware.WebmentionHeadMiddleware' to MIDDLEWARE::

        MIDDLEWARE = [
            ...
            'mentions.middleware.WebmentionHeadMiddleware',
        ]


2. Root project :code:`urls.py` ::

    urlpatterns = [
        ...
        path('webmentions/, include('mentions.urls')),
    ]


3. Include :code:`MentionableMixin` in the model(s) you want to support
   webmention functionality.

   IMPORTANT: Any models that include the mixin must also
   implement :code:`all_text` and :code:`get_absolute_url` methods::

    from mentions import MentionableMixin
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
