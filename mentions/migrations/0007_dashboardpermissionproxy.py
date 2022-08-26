# Generated by Django 4.1 on 2022-08-25 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "mentions",
            "0006_add_retryablemixin_pendingincomingwebmention_outgoingwebmentionstatus",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="DashboardPermissionProxy",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "permissions": (
                    (
                        "view_webmention_dashboard",
                        "Can view the webmention dashboard/status page.",
                    ),
                ),
                "managed": False,
                "default_permissions": (),
            },
        ),
    ]
