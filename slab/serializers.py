from rest_framework import serializers
from .models import Slab, Post, Answer, Comment, PostLikes, AnswerLikes, CommentLikes
from user.serializers import UserProfileSerializer

class SlabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slab
        fields = ('id', 'name', 'description', 'imoji', 'created_at')

class PostSerializer(serializers.ModelSerializer):
    slab = SlabSerializer(read_only=True)
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'slab', 'user', 'content', 'created_at')

class AnswerSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True)
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = Answer
        fields = ('id', 'post', 'user', 'content', 'created_at')

class CommentSerializer(serializers.ModelSerializer):
    answer = AnswerSerializer(read_only=True)
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'answer', 'user', 'content', 'created_at')

class PostLikesSerializer(serializers.ModelSerializer):

    post = PostSerializer(read_only=True)
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = PostLikes
        fields = ('id', 'post', 'user', 'created_at')

class AnswerLikesSerializer(serializers.ModelSerializer):
    answer = AnswerSerializer(read_only=True)
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = AnswerLikes
        fields = ('id', 'answer', 'user', 'created_at')

class CommentLikesSerializer(serializers.ModelSerializer):

    comment = CommentSerializer(read_only=True)
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = CommentLikes
        fields = ('id', 'comment', 'user', 'created_at')

        