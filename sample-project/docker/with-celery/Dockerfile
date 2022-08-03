FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

WORKDIR /var/www/static/
WORKDIR /src/
COPY . /src/
RUN --mount=type=cache,target=/root/.cache/pip pip install -e .[celery]

WORKDIR /usr/src/app
COPY ./sample-project .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

CMD sh /usr/src/app/docker/no-celery/entrypoint.sh
