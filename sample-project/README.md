# Sample project

This project demonstrates a working implementation of `django-wm`. Instructions for implementing it in your own project can be found [here](https://github.com/beatonma/django-wm/wiki/Guide_Getting-started) but this might be useful for reference too.

The main points of interest are `Article` and `Blog` in `sample_app/models.py`, and their corresponding `urlpatterns` entries in `sample_app/urls.py`.

The parent directory contains a `docker compose` configuration which starts up two instances of this project (one that uses Celery, one that does not). This can be a useful playground when developing a new feature for the `django-wm` library. Run `docker compose up --build` from the parent directory to try it out.
