from django.db import models
from character.models import Character
from user.models import UserProfile
from django.utils import timezone

# Create your models here.
class ChatSession(models.Model):
    TOPIC_CHOICES = [
        ("EmotionRegulation", "감정 조절 및 정서적 문제 해결"),
        ("DecisionMaking", "의사결정 및 선택"),
        ("Communication", "대인관계 및 커뮤니케이션"),
        ("SelfAwareness", "자기 인식 및 정체성"),
        ("MotivationProductivity", "동기부여 및 생산성/시간관리"),
        ("LearningStrategy", "학습/공부 전략 및 개념 이해"),
        ("None","자유 주제")
    ]
    character = models.ForeignKey(Character, on_delete=models.CASCADE, db_index=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_index = True)
    class Meta:
        indexes = [ models.Index(fields = ['user','character']),]
    summary = models.CharField(max_length = 50)
    topic = models.CharField(
        max_length=30,
        choices=TOPIC_CHOICES,
        default="None",
    )
    start_time = models.DateTimeField(default=timezone.now)
    time = models.DateTimeField()
    is_workflow = models.BooleanField(default=False)

class Message(models.Model):
    SENDER_CHOICES = [
        ("user", "사용자"),
        ("model", "인공지능")
    ]
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    order = models.IntegerField()
    is_workflow = models.BooleanField(default=False)

class Image(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='chat_images/')
    caption = models.CharField(max_length=255, blank=True, null=True)
    def delete(self, *args, **kwargs):
        # ① 파일 삭제
        if self.image:
            self.image.delete(save=False)
        # ② DB 레코드 삭제
        super().delete(*args, **kwargs)

class File(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='chat_files/')
    description = models.CharField(max_length=255, blank=True, null=True)
    def delete(self, *args, **kwargs):
    # ① 파일 삭제
        if self.file:
            self.file.delete(save=False)
        # ② DB 레코드 삭제
        super().delete(*args, **kwargs)

class Audio(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='audios')
    audio = models.FileField(upload_to='chat_audio/')
    transcript = models.TextField(blank=True, null=True)
    def delete(self, *args, **kwargs):
        # ① 파일 삭제
        if self.audio:
            self.audio.delete(save=False)
        # ② DB 레코드 삭제
        super().delete(*args, **kwargs)

class Citation(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='citations')
    text = models.TextField()
    uri = models.URLField()


