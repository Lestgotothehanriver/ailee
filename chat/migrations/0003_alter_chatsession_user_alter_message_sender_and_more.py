# Generated by Django 4.2 on 2025-06-25 05:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0002_chatsession_start_time"),
        ("user", "0002_userprofile"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatsession",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="user.userprofile"
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="sender",
            field=models.CharField(
                choices=[("user", "사용자"), ("model", "인공지능")], max_length=10
            ),
        ),
        migrations.AddIndex(
            model_name="chatsession",
            index=models.Index(
                fields=["user", "character"], name="chat_chatse_user_id_a06e6a_idx"
            ),
        ),
    ]
