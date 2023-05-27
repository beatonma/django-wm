FROM python:3.11-alpine AS common
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

RUN apk add curl

WORKDIR /var/www/static

WORKDIR /tmp/src/
COPY ./mentions ./mentions
COPY ./tests ./tests
COPY ./pyproject.toml .
COPY ./requirements.txt .
COPY ./setup.cfg .
COPY ./runtests.py .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /tmp/src/requirements.txt
RUN python /tmp/src/runtests.py

WORKDIR /project
COPY ./sample-project/requirements.txt /project
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /project/requirements.txt

# Pass a random CACHEBUST value to ensure data is updated and not taken from cache.
ARG CACHEBUST=0
RUN echo "CACHEBUST: $CACHEBUST"

WORKDIR /project

COPY ./sample-project/docker/entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]


################################################################################
FROM common AS with_celery

# Install extra dependencies but remove our package - will be mounted in compose
# to allow Django runserver to reload on code changes.
RUN --mount=type=cache,target=/root/.cache/pip pip install -e /tmp/src[celery,test]
RUN pip uninstall -y django-wm
RUN rm -r /tmp/src

CMD ["python", "manage.py", "sample_app_init"]


################################################################################
FROM common AS with_wagtail

# Install extra dependencies but remove our package - will be mounted in compose
# to allow Django runserver to reload on code changes.
RUN --mount=type=cache,target=/root/.cache/pip pip install -e /tmp/src[wagtail,test]
RUN pip uninstall -y django-wm
RUN rm -r /tmp/src

CMD ["python", "manage.py", "wagtail_app_init"]


################################################################################
FROM with_celery AS with_celery_celery

ENTRYPOINT celery -A sample_project worker -l info


################################################################################
FROM with_celery AS with_celery_cron

COPY ./sample-project/docker/with-celery/cron-schedule /
RUN crontab /cron-schedule

ENTRYPOINT crond -l 2 -f


################################################################################
FROM with_wagtail AS with_wagtail_cron

COPY ./sample-project/docker/with-wagtail/cron-schedule /
RUN crontab /cron-schedule

ENTRYPOINT crond -l 2 -f
