FROM python:3-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

RUN apk add --no-cache \
    bash

WORKDIR /var/www/static/
WORKDIR /src/
COPY . /src/
RUN --mount=type=cache,target=/root/.cache/pip pip install -e .[test]
RUN python runtests.py

WORKDIR /usr/src/app
COPY ./sample-project .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

RUN crontab /usr/src/app/docker/no-celery/cron-schedule

CMD bash /usr/src/app/docker/no-celery/entrypoint.sh
