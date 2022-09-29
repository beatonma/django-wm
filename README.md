# `django-wm`

[![Tests](https://github.com/beatonma/django-wm/actions/workflows/runtests.yml/badge.svg)](https://github.com/beatonma/django-wm/actions/workflows/runtests.yml) [![pypi package](https://badge.fury.io/py/django-wm.svg)](https://badge.fury.io/py/django-wm)

`django-wm` lets you add [Webmention](https://indieweb.org/Webmention) functionality to your Django project with minimal setup.


### Upgrading
Please check the [changelog](CHANGELOG.md) before upgrading, especially between major versions.

After upgrading remember to run the `makemigrations` and `migrate` management commands so that any changes in model/mixin definitions can be applied.


### Getting started
[Setup instructions](docs/getting_started.md).

[Code for an example project](https://github.com/beatonma/django-wm-example).

All done? You can use the [testing tool](https://beatonma.org/webmentions_tester/) to make sure it works.


### Features
- Endpoints:
  - `/webmention`: Receives incoming Webmentions from other sites.
  - `/webmention/get`: Used to retrieve Webmentions for a page on your site.  
    e.g. `/webmention/get?url=/my-article` will return any received Webmentions that target `/my-article` on your site.
    ```json5
    // /webmention/get?url=/my-article
    {
      "target_url": "https://my-site.org/my-article",
      "mentions": [
        {
          "hcard": {
            "name": "Jane Bloggs",
            "avatar": "https://gravatar.com/janebloggs",
            "homepage": "https://jane-bloggs-example.org"
          },
          "quote": null,
          "source_url": "https://jane-bloggs-example.org/some-article",
          "published": "2020-01-17T21:45:24.542Z",
          "type": "webmention"
        }
      ]
    }
    ```
  - `/webmention/dashboard/`: a simple overview of recent mentions (accessible with permission `mentions.view_webmention_dashboard` or publicly via `settings.WEBMENTIONS_DASHBOARD_PUBLIC`)

- `WebmentionHeadMiddleware` adds your `/webmention` endpoint to the headers of your pages so that it can be discovered by other sites.

- `{% webmentions_endpoint %}` template tag to include your `/webmention` endpoint to your Django templates <head> HTML element.

- `MentionableMixin` enables automatic submission of Webmentions to other sites when you mention them in your content.
