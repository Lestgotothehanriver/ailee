from rest_framework import serializers
from .models import ChatSession, Message
from character.models import Character

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ('id','character', 'user', 'summary', 'topic', 'time')

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('session', 'sender','message','order')