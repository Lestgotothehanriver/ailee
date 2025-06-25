from django.db import models

# Create your models here.

class Character(models.Model):
    name = models.CharField(max_length = 20)
    system_prompt = models.TextField()


