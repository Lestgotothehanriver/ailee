# Generated by Django 4.2 on 2025-06-27 08:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0003_delete_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="following",
            field=models.ManyToManyField(
                blank=True, related_name="followers", to="user.userprofile"
            ),
        ),
    ]
