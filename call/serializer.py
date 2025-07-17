from rest_framework import serializers
from .models import CallSession, Talk

class CallSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallSession
        fields = ('id', 'character', 'user', 'summary', 'start_time', 'time', 'is_workflow', 'message')

class TalkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Talk
        fields = ('session', 'sender', 'message', 'order', 'is_workflow')
        