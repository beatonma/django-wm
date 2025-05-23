# Generated by Django 4.1.1 on 2022-09-29 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mentions", "0009_alter_outgoingwebmentionstatus_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="hcard",
            name="avatar",
            field=models.URLField(
                blank=True, help_text="Link to their profile image", null=True
            ),
        ),
        migrations.AlterField(
            model_name="hcard",
            name="name",
            field=models.CharField(
                blank=True,
                help_text="Name of the person/organisation",
                max_length=50,
                null=True,
            ),
        ),
    ]
