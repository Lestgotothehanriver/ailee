# Generated by Django 4.2 on 2025-06-27 06:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0003_alter_chatsession_user_alter_message_sender_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatsession",
            name="is_workflow",
            field=models.BooleanField(default=False),
        ),
    ]
