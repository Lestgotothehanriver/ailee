from rest_framework import serializers
from .models import ChatSession, Message, Image, File, Audio
from character.models import Character


# 이미지
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']  # image는 URL로 변환됨

# 파일
class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'file']

# 오디오
class AudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audio
        fields = ['id', 'audio']

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ('id','character', 'user', 'summary', 'topic', 'time')

class MessageSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    files = FileSerializer(many=True, read_only=True)
    audios = AudioSerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = ('session', 'sender','message','order', 'images', 'files', 'audios')