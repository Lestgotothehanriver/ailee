from django.db import models
from user.models import UserProfile
from character.models import Character
# Create your models here.
class Content(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    title = models.CharField(max_length = 50)

class Content_message(models.Model):
    session = models.ForeignKey(Content, on_delete=models.CASCADE)
    message = models.TextField()
    order = models.IntegerField()

class ContentParticipation(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    time = models.DateTimeField()
    result = models.TextField()

