FROM python:3-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

RUN apk add --no-cache \
    bash

WORKDIR /var/www/static/

WORKDIR /usr/src/app
COPY ./sample-project .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

CMD bash /usr/src/app/docker/upgrade-check/entrypoint.sh
