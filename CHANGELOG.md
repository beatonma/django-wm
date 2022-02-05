# Changelog

# 2.1.0 (2022-02-05)

- Added setting `WEBMENTIONS_USE_CELERY` (boolean, default `True`)  
  **If `False`**:
  - `celery` does not need to be installed
  - New models `PendingIncomingWebmention` and `PendingOutgoingContent` are created to store the required 
    data for later batch-processing.
  - New management command: `manage.py pending_mentions` can be used to process these data.


- `/get` endpoint:
  - Now returns results for SimpleMention objects as well as Webmentions.
  - Added field `type` with value `webmention` or `simple` so they can be differentiated when displaying.

- Updated instructions for installation with or without celery.


# 2.0.0 (2022-02-02)


### Breaking Changes

- Migrations are now included. If you are upgrading from any `1.x.x` version please follow [these instructions](docs/upgrading_to_2.0.md) to avoid data loss. Thanks to **@GriceTurrble for providing these instructions.

- `requirements.txt` `celery` version updated to `5.2.2` due to [CVE-2021-23727](https://github.com/advisories/GHSA-q4xr-rc97-m4xx). If you are upgrading from `4.x` please follow the [upgrade instructions](https://docs.celeryproject.org/en/stable/history/whatsnew-5.0.html#upgrading-from-celery-4-x) provided by Celery.


### Web API changes:
- `/get` endpoint:
  - Removed `status` from JSON object - now uses HTTP response codes `200` if the target url was resolved correctly or `404` otherwise.
  - Missing HCards are now serialized as null instead of an empty dict
  
  
  ```json5
  // https://example.org/webmention/get?url=my-article
  // Old 1.x.x response
  {
    "status": 1,
    "target_url": "https://example.org/my-article",
    "mentions": [
      {
        "hcard": {},
        "quote": null,
        "source_url": "https://another-example.org/their-article",
        "published": "2020-01-17T21:45:24.542Z"
      }
    ]
  }
  ```

  ```json5
  // https://example.org/webmention/get?url=my-article
  // New 2.0.0 response with HTTP status 200 (or 404 if target_url does not exist)
  {
    "target_url": "https://example.org/my-article",
    "mentions": [
      {
        "hcard": null,
        "quote": null,
        "source_url": "https://another-example.org/their-article",
        "published": "2020-01-17T21:45:24.542Z"
      }
    ]
  }
  ```

### New 
- Use`{% webmention_endpoint %}` template tag to include your Webmentions endpoint in your Django template <head> to help other sites find it easily.
  ```html
  {% load webmention_endpoint %}
  <!-- my-template.html -->
  ...
  <head>
  {% webmention_endpoint %} <!-- Rendered as <link rel="webmention" href="/webmention/" /> -->
  </head>
  ...
  ```
