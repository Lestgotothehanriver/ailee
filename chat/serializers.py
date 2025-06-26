from rest_framework import serializers
from .models import ChatSession, Message
from character.models import Character

class ChatSerializer(serializers.ModelSerializer):
    model = ChatSession
    fields = ('character', 'user', 'summary', 'topic', 'time')

class MessageSerializer(serializers.ModelSerializer):
    model = Message
    fields = ('session', 'sender','message','order')