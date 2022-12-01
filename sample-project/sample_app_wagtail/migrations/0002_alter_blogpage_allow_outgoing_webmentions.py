# Generated by Django 4.1 on 2022-11-30 18:01

from django.db import migrations, models
import mentions.models.mixins.mentionable


class Migration(migrations.Migration):

    dependencies = [
        ('sample_app_wagtail', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpage',
            name='allow_outgoing_webmentions',
            field=models.BooleanField(default=mentions.models.mixins.mentionable._outgoing_default, verbose_name='allow outgoing webmentions'),
        ),
    ]
