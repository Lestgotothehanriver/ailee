# Generated by Django 4.2 on 2025-06-25 05:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatsession",
            name="start_time",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
