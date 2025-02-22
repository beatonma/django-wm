# Generated by Django 4.1.3 on 2022-11-09 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mentions", "0010_alter_hcard_avatar_alter_hcard_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pendingoutgoingcontent",
            name="text",
            field=models.TextField(
                help_text="Text that may contain mentionable links. (retrieved via MentionableMixin.get_content_html())"
            ),
        ),
    ]
