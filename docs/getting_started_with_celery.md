# Using Celery

> As of version `2.1.0`, celery is recommended but [no longer required](getting_started_without_celery.md).

It is recommended that you use [`celery`](https://docs.celeryproject.org/)  to handle Webmention processing asynchronously. This document provides instructions for setting up `celery` with `rabbitmq` in an Ubuntu-based environment.

```shell
# Install django-wm with celery from PyPI.
pip install django-wm[celery]
python manage.py migrate

# Install RabbitMQ.
sudo apt install rabbitmq-server

# Create a user for the celery process and make sure it can access your database
sudo useradd -N -M --system -s /bin/bash celery  # Create a user for celery
sudo usermod -a -G www-data celery  # Add celery user to (e.g.) www-data group
```


Create `celery.py` in your project directory. e.g.
```
myproject
├── myproject
│   ├── __init__.py
│   ├── celery.py     <-- HERE
│   ├── settings.py
│   ├── urls.py
│   └── ...etc
├── myapp
└── manage.py
```

...and add the contents:

```python
# celery.py
from __future__ import absolute_import

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

Finally, run the celery process. You will normally want to run this as a daemon process - see
[here](https://docs.celeryproject.org/en/stable/userguide/daemonizing.html) for details.

```shell
# Run celery as the celery user we created above.
sudo -u celery env/bin/celery --app myproject worker
```

### Links

- Celery: https://docs.celeryproject.org/

- Daemonizing Celery: https://docs.celeryproject.org/en/stable/userguide/daemonizing.html

- Using RabbitMQ: https://docs.celeryproject.org/en/stable/getting-started/backends-and-brokers/rabbitmq.html#broker-rabbitmq

# All done?

Go back and follow the rest of the instructions for [django-wm](getting_started.md#project-code)
