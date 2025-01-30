# Changelog

> [!NOTE]
> Release notes are also available on the [wiki](https://github.com/beatonma/django-wm/wiki/Releases).


## 4.1.2 (2025-01-30)
- Fixed [#54](https://github.com/beatonma/django-wm/issues/54): Broken on `wagtail>=6.2`.
  - Issue: In `wagtail==6.2`, the implementation of `RoutablePageMixin.route` was changed to add the `routable_resolver_match` attribute to the given request object. `get_model_for_url_by_wagtail` previously called that method with `request=None` (because there is no relevant request object available at the time webmentions are processed), so trying to set that attribute on the request fails.
  - Fix: `get_model_for_url_by_wagtail` now creates and passes a dummy instance of `HttpRequest` when calling that method.


## 4.1.1 (2024-02-10)

> [!WARNING]
> `python manage.py migrate` required for new fields.  

- Added `Webmention.has_been_read: bool` field.  
  - New context processor `mentions.context_processors.unread_webmentions` adds `unread_webmentions` field to template context, containing the queryset of unread Webmention objects.
  - Added admin actions for marking as read/unread.  
  
- New `objects` manager for Webmention with some common filters and actions.  
  
- New settings for allowing or disabling webmentions to/from a set of domains:  
  - <a href="Settings#WEBMENTIONS_DOMAINS_INCOMING_ALLOW">`WEBMENTIONS_DOMAINS_INCOMING_ALLOW: Iterable[str] = None`</a>  
  - <a href="Settings#WEBMENTIONS_DOMAINS_INCOMING_DENY">`WEBMENTIONS_\DOMAINS_INCOMING_DENY: Iterable[str] = None`</a>  
  - <a href="Settings#WEBMENTIONS_DOMAINS_OUTGOING_ALLOW">`WEBMENTIONS_DOMAINS_OUTGOING_ALLOW: Iterable[str] = None`</a>  
  - <a href="Settings#WEBMENTIONS_DOMAINS_OUTGOING_DENY">`WEBMENTIONS_DOMAINS_OUTGOING_DENY: Iterable[str] = None`</a>

- New settings for tags that can be added to your HTML links to allow/disable sending webmentions for just that specific link. (Overrides above allow/deny lists)
  - <a href="Settings#WEBMENTIONS_DOMAINS_OUTGOING_TAG_ALLOW">`WEBMENTIONS_DOMAINS_OUTGOING_TAG_ALLOW: str = None`</a>  
  - <a href="Settings#WEBMENTIONS_DOMAINS_OUTGOING_TAG_DENY">`WEBMENTIONS_DOMAINS_OUTGOING_TAG_DENY: str = None`</a>  


## 4.0.4 (2024-02-02)
- Resolves [#53](https://github.com/beatonma/django-wm/issues/53): Compatibility with dependency `mf2py>=2.0`.


## 4.0.2 (2023-05-27)
- Resolves [#50](https://github.com/beatonma/django-wm/issues/50): broken search field on QuotableAdmin.
- Added tests for admin pages to avoid that sort of thing happening again.
- Minor touch-ups for the admin pages.
  - Source and target URL fields are now read-only.
  - Added appropriate search fields and list filters for each model.
  - `quote` field now uses a textarea widget for comfier editing.



## 4.0.1 (2022-12-22)

- Added management command `mentions_reverify [filters ...] [--all]`
  - Allows you to reprocess received Webmentions to see if they are still 'live'.
  - Accepts a space-separated list of `field=value` queryset filters, or `--all` to reprocess all of them.

- Added management command `mentions_pending` to replace `pending_mentions` for naming consistency with other commands.
  - `pending_mentions` still works though.

- Now compatible with `Wagtail>=3.0.3` (previously `>=4.0`).
  - `mentions_wagtail_path` still requires `>=4.0`: use `mentions_wagtail_route` or `mentions_wagtail_re_path`.


## 4.0.0 (2022-11-25)

> This update alters fields on `MentionableMixin` so you will need to run `makemigrations` and `migrate` after upgrading!

- `MentionableMixin`:
  - `allow_outgoing_webmentions` default now configurable via `settings.WEBMENTIONS_ALLOW_OUTGOING_DEFAULT`.
  - Removed `slug` field. If you use this field you can restore the previous behaviour by adding the following to your model.

    ```python
    class MyModel(MentionableMixin, models.Model):
        slug = models.SlugField(unique=True)
  
        @classmethod
        def resolve_from_url_kwargs(cls, slug, **url_kwargs):
            return cls.objects.get(slug=slug)
    ```
  - Deprecated method`all_text`, replaced by `get_content_html`. Overriding `all_text` still works for now but will log a warning asking you to rename the method.


- Moved template files to `mentions` sub-directory. If you have custom overrides of these templates in your root `templates/` directory please move them to `templates/mentions/`.


- Added user agent header to all network requests.
  - Customisable via `settings.WEBMENTIONS_USER_AGENT: str`.


- Admin-facing strings are now translatable.


- Added `urlpatterns` helper functions `mentions_path`, `mentions_re_path` for (hopefully) simpler setup.
  - More straightforward view-to-model mapping.
  - Removes the need to implement `resolve_from_url_kwargs` on your MentionableMixin implementation.
  - See [the wiki](https://github.com/beatonma/django-wm/wiki/Guide_Using-MentionableMixin#urlpatterns) for example setup instructions.

  
- Support for [Wagtail](https://wagtail.org/).
  - `Page` models should implement `MentionableMixin` as usual.
  - `RoutablePageMixin` should use the new `@mentions_wagtail_path`, `@mentions_wagtail_re_path` decorators in place of the Wagtail equivalents `@path`, `@re_path`.
    - These work essentially the same `mentions_path` and `mentions_re_path`.
  - If using RichTextField call `richtext` on any RichTextField values in `get_content_html`:
  ```python
  from wagtail.templatetags.wagtailcore_tags import richtext
  
  class MyModel(MentionableMixin, Page):
      ...
      def get_content_html(self) -> str:
          return f"{richtext(self.overview)} {richtext(self.body)}"
  ```


- Wiki pages are now [live](https://github.com/beatonma/django-wm/wiki/)! These will be kept up-to-date going forwards but may not be useful for pre-4.0 versions.


- Fix: Relative URLs in `h-card` homepage or avatar are now resolved to absolute URLs.


## 3.1.1 (2022-10-26)

Fixes [#43](https://github.com/beatonma/django-wm/issues/43): outgoing webmention being resubmitted continuously.


## 3.1.0 (2022-10-06)

- Resolves [#38](https://github.com/beatonma/django-wm/issues/38): Revalidate target URLs when handling pending mentions
  - Should be unnecessary generally (they are also validated at discovery time when parsed from HTML) but important if validation checks are updated.

- Resolves [#41](https://github.com/beatonma/django-wm/issues/41): Find correct endpoint when multiple `link`s in HTTP header.

- Added `settings.WEBMENTIONS_INCOMING_TARGET_MODEL_REQUIRED` \[`bool` | default=`False`]. If `True`, incoming mentions are only accepted if their target resolves to a `MentionableMixin` instance.

- Added `settings.WEBMENTIONS_ALLOW_SELF_MENTIONS` \[`bool` | default=`True`].
  - If `False`, outgoing links that target your own domain (as specified by `settings.DOMAIN_NAME`) will be ignored - you will only submit mentions to other domains.
  - If `True`, outgoing links that use a relative path (e.g. `href="/article/1/"`) are now supported.

- Fix: WebmentionHeadMiddleware no longer overwrites existing links in HTTP header when adding webmention endpoint.

- Fix: Webmention 'notes' no longer persists across instances.


## 3.0.0 (2022-09-29)

### Upgrade warning

If upgrading from an older version please be aware of these changes:
- Unused `MentionableMixin.allow_incoming_webmentions` field has been removed.
- Any existing instances of `PendingIncomingWebmention` and `PendingOutgoingContent` will be deleted.
  - These models have new constraints so it is necessary to recreate them.
  - If this is problematic for you please don't upgrade yet. Contact me or create an issue and I will make a tool to persist these between versions.

### Changes

Thanks to @philgyford for reporting most of the issues referenced here.

- Resolves [#25](https://github.com/beatonma/django-wm/issues/25).
  - Added `QuotableMixin.post_type` field.

  - Incoming webmentions are now checked for the following microformat
    properties that describe the type of mention they are:
      - `u-bookmark-of`
      - `u-like-of`
      - `u-listen-of`
      - `u-in-reply-to`
      - `u-repost-of`
      - `u-translation-of`
      - `u-watch-of`

  - The `/webmention/get` endpoint serializes these values in the `type`
    field respectively as:
    - `bookmark`
    - `like`
    - `listen`
    - `reply`
    - `repost`
    - `translation`
    - `watch`
    - If no specific `type` is specified this defaults to `webmention`.

- Resolves [#30](https://github.com/beatonma/django-wm/issues/30)
  - Added `MentionableMixin.should_process_webmentions() -> bool` method to enable custom logic.

- Resolves [#31](https://github.com/beatonma/django-wm/issues/31)
  - Success message now rendered via template, enabling override by user.

- Resolves [#32](https://github.com/beatonma/django-wm/issues/32)
  - Same-page #anchor links no longer treated as webmention targets.

- Resolves [#33](https://github.com/beatonma/django-wm/issues/33), [#34](https://github.com/beatonma/django-wm/issues/34)
  - Much improved parsing of `h-card`.
    - Now tries to find an`h-card` that is directly related to the mention link (embedded in `p-author` of a parent `h-entry` or `h-feed` container).
    - If that doesn't yield a result, try to find a top-level `h-card` on the page.
  - Removed `HCard.from_soup()` classmethod. Parsing logic moved to `tasks.incoming.parsing` package.

- Resolves [#36](https://github.com/beatonma/django-wm/issues/36)
  - Added constraints to `PendingIncomingWebmention` and `PendingOutgoingContent` to avoid duplication.
    - **Warning**: If updating from an older version of `django-wm` this will delete any existing `Pending...` model instances.
  - Request timeouts are now handled gracefully.
  - `PendingIncomingWebmention` and `OutgoingWebmentionStatus` now implement the new `RetryableMixin`.
  - Reworked webmention processing tasks to allow failed webmentions to be retried periodically.
    - See settings `WEBMENTIONS_MAX_RETRIES`, `WEBMENTIONS_RETRY_INTERVAL`, `WEBMENTIONS_TIMEOUT` below for customisation details.

- New `dashboard/` view: a simple overview of recent mentions.
  - Shows the latest instances of `Webmention`, `OutgoingWebmentionStatus`, `PendingIncomingWebmention`, `PendingOutgoingContent` and info on their current status.
  - By default, restricted to users with `mentions.view_webmention_dashboard` permission.
  - Can be made public via `settings.WEBMENTIONS_DASHBOARD_PUBLIC = True`.

- New optional settings:
  - `settings.WEBMENTIONS_TIMEOUT` \[`float` | default=`10`] specifies the time (in seconds) to wait for network calls to resolve.
  - `settings.WEBMENTIONS_RETRY_INTERVAL` \[`int` | default=`600`] specifies the minimum time (in seconds) to wait before retrying to process a webmention.
  - `settings.WEBMENTIONS_MAX_RETRIES` \[`int` | default=`5`] specifies how many times we can attempt to process a mention before giving up.
  - `settings.WEBMENTIONS_DASHBOARD_PUBLIC` \[`bool` | default=`False`] specifies whether the the `dashboard/` view can be viewed by anyone. If `False` (default), the `dashboard/` view is only available to users with `mentions.view_webmention_dashboard` permission.

- `WebmentionHeadMiddleware`
  - Removed port from generated endpoint URL in HTTP headers as `request.META.SERVER_PORT` may not be reliable depending on reverse proxy configuration.

- `MentionableMixin`:
  - `mentions()` is now a method, not a property.
  - Removed field `allow_incoming_webmentions` as it has never been used for anything.

- Streamlined template tags
  - `{% load webmentions_endpoint %}` replaced by `{% load webmentions %}`.
  - `{% webmention_endpoint %}` replaced by `{% webmentions_endpoint %}` (used in HTML `<head>`).
  - New tag `{% webmentions_dashboard %}` creates a <a>link</a> to your `webmentions/dashboard/` view.


## 2.3.0 (2022-03-28)

Resolves [#28](https://github.com/beatonma/django-wm/issues/28)

New MentionableMixin classmethod: `resolve_from_url_kwargs(**url_kwargs)`
- This method receives captured parameters from an `urlpatterns` path.
- By default, it uses `<slug:slug>` to look up your object by a unique `slug` field.
- You can customize this by overriding the classmethod in your
  MentionableMixin implementation

  e.g.
    ```python
    # urls.py
    urlpatterns = [
        path(
            fr"<int:year>/<int:month>/<int:day>/<slug:post_slug>/",
            MyBlogPostView.as_view(),
            name="my-blog",
            kwargs={
                "model_name": "myapp.MyBlog",
            },
        ),
    ]

    # models.py
    class MyBlog(MentionableMixin, models.Model):
        date = models.DateTimeField(default=timezone.now)
        slug = models.SlugField()
        content = models.TextField()

        def all_text(self):
            return self.content

        def get_absolute_url(self):
            return reverse(
                "my-blog",
                kwargs={
                    "year": self.date.strftime("%Y"),
                    "month": self.date.strftime("%m"),
                    "day": self.date.strftime("%d"),
                    "post_slug": self.slug,
                }
            )

        @classmethod
        def resolve_from_url_kwargs(cls, year, month, day, post_slug, **url_kwargs):
            return cls.objects.get(
                date__year=year,
                date__month=month,
                date__day=day,
                slug=post_slug,
            )

    ```

`mentions.resolution.get_model_for_url_path` now delegates to
`MentionableMixin.resolve_from_url_kwargs` to resolve captured URL
parameters to a model instance.


## 2.2.0 (2022-03-26)

Merges [#24](https://github.com/beatonma/django-wm/pull/24): `QuotableMixin.published` can now be overriden - thanks [@garrettc](https://github.com/garrettc).
Fixes [#26](https://github.com/beatonma/django-wm/issues/26): `requests` 2.20 or greater (until version 3) are now allowed. Likewise for `beautifulsoup4` 4.6 and `mf2py` 1.1.

Added `get_mentions_for_view(HttpRequest) -> Iterable[QuotableMixin]` convenience method. This may be used to retrieve mentions for rendering directly in a Django template, as an alternative to using the `webmention/get` endpoint from a frontend script.


## 2.1.1 (2022-02-07)

Fix: Test view defined in main urlpatterns.


## 2.1.0 (2022-02-05)

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


## 2.0.0 (2022-02-02)

### Breaking Changes

- Migrations are now included. If you are upgrading from any `1.x.x` version please follow [these instructions](https://github.com/beatonma/django-wm/wiki/Guide_Upgrading-to-2.0) to avoid data loss. Thanks to **@GriceTurrble for providing these instructions.

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
