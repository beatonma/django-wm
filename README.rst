Mentions
===

Mentions lets you add Webmention functionality to any model with minimal
setup.

Setup
-----
1. Add "mentions" to your INSTALLED_APPS setting::

    INSTALLED_APPS = [
        ...
        'mentions',
    ]

2. Include the URLconf if your project urls.py::

    path('{}, include('mentions.urls')),

3. Include `MentionableMixin` in the model(s) you want to support
   webmention functionality.

   IMPORTANT: Any models that include the mixin must also
   implement `all_text()`::

    from mentions import MentionableMixin
    ...

    class MyModel(MentionableMixin, models.Model):
        ...
        def all_text(self):
            return f'{self.introduction} {self.content}'

4. Run `python manage.py migrate` to create/update models.
