# Generated by Django 4.2 on 2025-05-28 05:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("character", "0001_initial"),
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChatSession",
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
                ("summary", models.CharField(max_length=50)),
                (
                    "topic",
                    models.CharField(
                        choices=[
                            ("EmotionRegulation", "감정 조절 및 정서적 문제 해결"),
                            ("DecisionMaking", "의사결정 및 선택"),
                            ("Communication", "대인관계 및 커뮤니케이션"),
                            ("SelfAwareness", "자기 인식 및 정체성"),
                            ("MotivationProductivity", "동기부여 및 생산성/시간관리"),
                            ("LearningStrategy", "학습/공부 전략 및 개념 이해"),
                            ("None", "자유 주제"),
                        ],
                        default="None",
                        max_length=30,
                    ),
                ),
                ("time", models.DateTimeField()),
                (
                    "character",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="character.character",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="user.user"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Message",
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
                (
                    "sender",
                    models.CharField(
                        choices=[("User", "사용자"), ("System", "인공지능")], max_length=10
                    ),
                ),
                ("message", models.TextField()),
                ("order", models.IntegerField()),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="chat.chatsession",
                    ),
                ),
            ],
        ),
    ]
