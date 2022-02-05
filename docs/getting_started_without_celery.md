# Without Celery

> As of version `2.1.0`, celery is [recommended](getting_started_with_celery.md) but no longer required.

Install `django-wm` from PyPI:

```shell
pip install django-wm
python manage.py migrate
```

In your project `settings.py` file add a new line with:

```python
WEBMENTIONS_USE_CELERY = False
```

Run `manage.py pending_migrations` to batch-process any pending Webmentions.


### How it works

Processing a webmention requires a number of network calls to the other (sending/receiving) server, any of which might have errors or take a while to complete. When `celery` is disabled, incoming and outgoing Webmentions will store required data in your database so they can be processed separately.

- When you save a model that implements `MentionableMixin`, a PendingOutgoingContent object will be created.
- When an incoming Webmention is received, a PendingIncomingWebmention object will be created.

You can then batch-process these using a Django management command:
```shell
python manage.py pending_mentions
```

You may want to schedule this to run regularly via something like `cron`.

# All done?

Go back and follow the rest of the instructions for [django-wm](getting_started.md#project-code)
