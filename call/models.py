from django.db import models
from chat.models import Message
from character.models import Character
from user.models import UserProfile
from django.utils import timezone

# Create your models here.
class CallSession(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, db_index=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_index = True)
    class Meta:
        indexes = [ models.Index(fields = ['user','character']),]
    summary = models.CharField(max_length = 50)
    start_time = models.DateTimeField(default=timezone.now)
    time = models.DateTimeField()
    is_workflow = models.BooleanField(default=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='call_sessions', null=True, blank=True)

class Talk(models.Model):
    SENDER_CHOICES = [
        ("user", "사용자"),
        ("model", "인공지능")
    ]
    session = models.ForeignKey(CallSession, on_delete=models.CASCADE, related_name='talks')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    order = models.IntegerField()
    is_workflow = models.BooleanField(default=False)

class Audio(models.Model):
    talk = models.ForeignKey(Talk, on_delete=models.CASCADE, related_name='audios')
    audio = models.FileField(upload_to='chat_audio/')
    transcript = models.TextField(blank=True, null=True)
    def delete(self, *args, **kwargs):
        # ① 파일 삭제
        if self.audio:
            self.audio.delete(save=False)
        # ② DB 레코드 삭제
        super().delete(*args, **kwargs)