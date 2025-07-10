from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'id', 'gmail', 'password', 'name', 'main_character',
            'country', 'birth_date', 'activation_time',
            'i_e', 'n_s', 't_f', 'p_j',
            'ailee_chat_count', 'joon_chat_count',
            'nick_chat_count', 'chad_chat_count', 'rin_chat_count',
            'emotion_count', 'decision_count', 'social_count',
            'identity_count', 'motivation_count', 'learning_count', 
            'following'
        )
        read_only_fields = ('id',)  # 추천
        extra_kwargs     = {'password': {'write_only': True}}

    def create(self, validated_data):
        # 비밀번호 해싱
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
