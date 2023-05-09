FROM python:3.11-alpine AS common
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

RUN apk add curl

WORKDIR /var/www/static

WORKDIR /tmp/src/
COPY ./mentions /tmp/src/mentions
COPY ./tests /tmp/src/tests
COPY ./pyproject.toml /tmp/src/
COPY ./requirements.txt /tmp/src/
COPY ./setup.cfg /tmp/src/
COPY ./runtests.py /tmp/src/
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /tmp/src/requirements.txt
RUN python /tmp/src/runtests.py

WORKDIR /project
COPY ./sample-project/requirements.txt /project
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /project/requirements.txt

# Pass a random CACHEBUST value to ensure data is updated and not taken from cache.
ARG CACHEBUST=0
RUN echo "CACHEBUST: $CACHEBUST"

WORKDIR /project


################################################################################
FROM common AS with_celery

RUN --mount=type=cache,target=/root/.cache/pip pip install -e /tmp/src[celery,test]
COPY ./sample-project/docker/with-celery/entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]


################################################################################
FROM common AS with_wagtail

RUN --mount=type=cache,target=/root/.cache/pip pip install -e /tmp/src[wagtail,test]
COPY ./sample-project/docker/with-wagtail/entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]


################################################################################
FROM with_celery AS with_celery_celery

ENTRYPOINT []
CMD celery -A sample_project worker -l info


################################################################################
FROM with_celery AS with_celery_cron

COPY ./sample-project/docker/with-celery/cron-schedule /
RUN crontab /cron-schedule

ENTRYPOINT []
CMD crond -l 2 -f


################################################################################
FROM with_wagtail AS with_wagtail_cron

COPY ./sample-project/docker/with-wagtail/cron-schedule /
RUN crontab /cron-schedule

ENTRYPOINT []
CMD crond -l 2 -f
