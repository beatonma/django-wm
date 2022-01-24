# Upgrading to v1.4+

The following guide seeks to alleviate potential issues when upgrading from `django-wm<1.4` to **v1.4.0** and beyond.

⚠ **Breaking change** ⚠

Prior versions of `django-wm` omitted [migration files] for the `mentions` app that this package provides. This was an oversight: when running `manage.py makemigrations`, one or more migration files would be generated within the `django-wm` package installation. This can cause issues when/if `django-wm` is updated with changes to its concrete models.

Starting in **v1.4.0**, migrations for `mentions` app's *concrete* models - models that are NOT [abstract base classes] - will be included with the package distribution. This way, new changes to those concrete models can be smoothly migrated in any environment that uses `django-wm`.

The following models are affected by the change:

- `mentions.HCard`
- `mentions.OutgoingWebmentionStatus`
- `mentions.SimpleMention`
- `mentions.Webmention`

**Notes**:

- **Database tables created by mentions models in v1.3.0 are identical to those created with v1.4.0**. Any database environment with up-to-date model migrations as of **v1.3.0** should be able to upgrade to **v1.4.0** with no impacts on data or database schemas.
- **Model *mixins* are not affected**. Mixins are [abstract base classes], and do not generate migrations in the `mentions` app under any circumstances.
- **Models that inherit from mixins are also not affected**. You do not need to generate new migrations for your own apps if you inherit from these mixin classes.

## Manually upgrading migrations in a running application

If you are uncertain if your app will be adversely affected by this change, you may take the following steps to safely migrate your existing environment:

⚠ **Do not** upgrade the `django-wm` package yet! You will need the existing migration files from your current installation.

1. Navigate to the Python installation or virtual environment where `django-wm` is installed, and locate the `lib/site-packages/mentions` directory (where the installed code for this package resides).
2. Copy the `migrations` directory and its contents to a safe location *outside* the Python virtual environment.

   - The migration files here will be ones your Django project generated using the `makemigrations` command in **v1.3.0** and below.

3. Upgrade `django-wm` to **v1.4.0**, using `pip install --upgrade django-wm==1.4.0`.
4. Within `lib/site-packages/mentions/migrations`, rename the new `0001_initial.py` migration to `initial.out`.

   - This way, Django will not see it when running `migrate` later.
   - You can test this by running `manage.py showmigrations mentions` : it should report `(no migrations)`.

5. Copy your *old* migration files back to `lib/site-packages/mentions/migrations`.
6. In your Django project, run `manage.py makemigrations mentions`.

   - This may create a new migration in `lib/site-packages/mentions/migrations`, based on differences between your existing version of `django-wm` and **v1.4.0**.
   - 👉 This step is the key! If there were unforeseen differences between your existing app and the newer version of `django-wm`, you will now be able to migrate upwards without data loss.

7. Run `manage.py migrate` as you normally would to update your database schema.

   - ✔ Now your database should exactly match the expected schema for `django-wm==1.4.0`.

8. Run `manage.py migrate mentions 0001 --fake`.

   - With `--fake`, no changes are to your database schema made. Only the `django_migrations` table - where Django tracks which migrations have been run in against *that* database - is altered.
   - This tricks the application into thinking no other migrations have been run for the `mentions` app beyond `0001_initial`.

9. Remove your old migration files from `lib/site-packages/mentions/migrations` (don't remove your `initial.out` file from before!)
10. Rename the `initial.out` file - the "real" migration file - back to `0001_initial.py`.

    - If you did accidentally delete this file, don't panic: simply uninstall/reinstall `django-wm==1.4.0` again to get a new copy of this migration file.

11. Test that no other changes are needed by running `makemigrations`, `showmigrations`, and/or `migrate` commands to ensure your application database is up-to-date.

🎉 That's it! You are now ready to use and upgrade `django-wm` safely in the future, along with any migration files for new changes to its own concrete models. 😊

[migration files]: https://docs.djangoproject.com/en/4.0/topics/migrations/
[abstract base classes]: https://docs.djangoproject.com/en/4.0/topics/db/models/#abstract-base-classes
