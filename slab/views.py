from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Slab, Post, Answer, Comment, PostLikes, AnswerLikes, CommentLikes
from .serializers import SlabSerializer, PostSerializer, AnswerSerializer, CommentSerializer, PostLikesSerializer, AnswerLikesSerializer, CommentLikesSerializer
# Create your views here.


class UserSlabView(APIView):
    """
    유저 슬랩 뷰
    GET 요청을 처리하여 메인 페이지 포스트들을 렌더링합니다.
    URL: api/slabs/users/<int:user_id>/
    """

    def get(self, request, user_id):
        return None
        

class SlabPostView(APIView):
    """
    슬랩 뷰
    GET 요청을 처리하여 특정 슬랩의 Post들을 렌더링합니다.
    URL: api/slabs/<int:slab_id>/posts/
    """
    def get(self, request, slab_id):
        is_time_order = request.GET.get('is_time_order', False)
        if is_time_order:
            # 시간 순서로 정렬된 Post들을 반환하는 로직
            pass
        else:
            # 인기 순으로 정렬된 Post들을 반환하는 로직
            pass

class PostDetailView(APIView):

    """
    POST 요청을 처리하여 새로운 Post를 생성합니다.
    PUT 요청을 처리하여 특정 Post를 수정합니다.
    DELETE 요청을 처리하여 특정 Post를 삭제합니다.
    URL: api/slabs/posts/<int:post_id>/
    """

    def post(self, request, post_id):
        is_workflow = request.GET.get('is_workflow', False)
        if is_workflow:
            # 워크플로우를 사용하는 Post 생성 로직
            pass
        else:
            # 일반 Post 생성 로직
            pass

    def put(self, request, post_id):
        # 특정 Post를 수정하는 로직
        content = request.data.get('content', '')
        post = Post.objects.get(id=post_id)
        post.content = content
        post.save()
        return HttpResponse(status=204)

    def delete(self, request, post_id):
        # 특정 Post를 삭제하는 로직
        try: 
            post = Post.objects.get(id=post_id)
            post.delete()
            return HttpResponse(status=204)

        except Post.DoesNotExist:
            return HttpResponse(status=404)

class PostAnswerView(APIView):
    """
    GET 요청을 처리하여 특정 Post의 모든 Answers를 렌더링합니다.
    URL: api/slabs/posts/<int:post_id>/answers/
    """
    def get(self, request, post_id):
        post = Post.objects.get(id=post_id)
        answer = post.answers.all().order_by('-created_at')
        serialzer = AnswerSerializer(answer, many=True)
        return HttpResponse(serialzer.data, content_type='application/json')
        
        
class AnswerDetailView(APIView):
    """
    POST 요청을 처리하여 새로운 Answer를 생성합니다.
    PUT 요청을 처리하여 특정 Answer를 수정합니다.
    DELETE 요청을 처리하여 특정 Answer를 삭제합니다.
    URL: api/slabs/answers/<int:answer_id>/
    """
    def post(self, request, answer_id):
        content = request.data.get('content', '')
        post_id = request.data.get('post_id', None)
        user_id = request.data.get('user_id', None)
        if post_id and user_id:
            post = Post.objects.get(id=post_id)
            user = User.objects.get(id=user_id)
            answer = Answer.objects.create(post=post, user=user, content=content)
            serializer = AnswerSerializer(answer)
            return Response(serializer.data, status=201)

    def put(self, request, answer_id):
        answer = Answer.objects.get(id=answer_id)
        content = request.data.get('content', '')
        answer.content = content
        answer.save()
        return HttpResponse(status=204)

    def delete(self, rerquest, answer_id):
        try:
            answer = Answer.objects.get(id=answer_id)
            answer.delete()
            return HttpResponse(status=204)
        except Answer.DoesNotExist:
            return HttpResponse(status=404)
    

class AnswerCommentView(APIView):
    """
    GET 요청을 처리하여 특정 Answer의 모든 Comments를 렌더링합니다.
    URL: api/slabs/answers/<int:answer_id>/comments/
    """
    def get(self, request, answer_id):
        answer = Answer.objects.get(id=answer_id)
        comments = answer.comments.all().order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=200)

class CommentDetailView(APIView):
    """
    Comment 뷰
    POST 요청을 처리하여 새로운 Comment를 생성합니다.
    PUT 요청을 처리하여 특정 Comment를 수정합니다.
    DELETE 요청을 처리하여 특정 Comment를 삭제합니다.
    URL: api/slabs/comments/<int:comment_id>/
    """
    
    def post(self, request, comment_id):
        content = request.data.get('content', '')
        answer_id = request.data.get('answer_id', None)
        user_id = request.data.get('user_id', None)
        if answer_id and user_id:
            answer = Answer.objects.get(id=answer_id)
            user = User.objects.get(id=user_id)
            comment = Comment.objects.create(answer=answer, user=user, content=content)
            serializer = CommentSerializer(comment)
            return Response(serializer.data, status=201)

    def put(self, request, comment_id):
        comment = Comment.objects.get(id=comment_id)
        content = request.data.get('content', '')
        comment.content = content
        comment.save()
        return HttpResponse(status=204)

    def delete(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
            comment.delete()
            return HttpResponse(status=204)
        except Comment.DoesNotExist:
            return HttpResponse(status=404)

class PostLikesView(APIView):
    """
    Post Likes 뷰
    GET 요청을 처리하여 특정 Post의 모든 Likes를 렌더링합니다.
    POST 요청을 처리하여 특정 Post에 Like를 추가합니다.
    DELETE 요청을 처리하여 특정 Post의 Like를 제거합니다.
    URL: api/slabs/posts/<int:post_id>/likes/
    """ 
    def get(self, request, post_id):
        post = Post.objects.get(id=post_id)
        likes = post.likes.all().order_by('-created_at')
        serializer = PostLikesSerializer(likes, many=True)
        return Response(serializer.data, status=200)

    def post(self, request, post_id):
        user_id = request.data.get('user_id', None)
        post = Post.objects.get(id=post_id)
        user = User.objects.get(id=user_id)
        like = PostLikes.objects.create(post=post, user=user)
        return Response({"message": "Like added successfully"}, status=201)
    
    def delete(self, request, post_id):
        user_id = request.data.get('user_id', None)
        try:
            post = Post.objects.get(id=post_id)
            like = PostLikes.objects.get(post=post, user__id=user_id)
            like.delete()
            return HttpResponse(status=204)
        except PostLikes.DoesNotExist:
            return HttpResponse(status=404)

class AnswerLikesView(APIView):
    """
    Answer Likes 뷰
    GET 요청을 처리하여 특정 Answer의 모든 Likes를 렌더링합니다.
    POST 요청을 처리하여 특정 Answer에 Like를 추가합니다.
    DELETE 요청을 처리하여 특정 Answer의 Like를 제거합니다.
    URL: api/slabs/answers/<int:answer_id>/likes/
    """
    def get(self, request, answer_id):
        answer = Answer.objects.get(id=answer_id)
        likes = answer.likes.all().order_by('-created_at')
        serializer = AnswerLikesSerializer(likes, many=True)
        return Response(serializer.data, status=200)

    def post(self, request, answer_id):
        user_id = request.data.get('user_id', None)
        answer = Answer.objects.get(id=answer_id)
        user = User.objects.get(id=user_id)
        like = AnswerLikes.objects.create(answer=answer, user=user)
        return Response({"message": "Like added successfully"}, status=201)

    def delete(self, request, answer_id):
        user_id = request.data.get('user_id', None)
        answer = Answer.objects.get(id=answer_id)
        user = User.objects.get(id=user_id)
        try:
            like = AnswerLikes.objects.get(answer=answer, user=user)
            like.delete()
            return HttpResponse(status=204)
        except AnswerLikes.DoesNotExist:
            return HttpResponse(status=404)


class CommentLikesView(APIView):
    """
    Comment Likes 뷰
    GET 요청을 처리하여 특정 Comment의 모든 Likes를 렌더링합니다.
    POST 요청을 처리하여 특정 Comment에 Like를 추가합니다.
    DELETE 요청을 처리하여 특정 Comment의 Like를 제거합니다.
    URL: api/slabs/comments/<int:comment_id>/likes/
    """

    def get(self, request, comment_id):
        comment = Comment.objects.get(id=comment_id)
        likes = comment.likes.all().order_by('-created_at')
        serializer = CommentLikesSerializer(likes, many=True)
        return Response(serializer.data, status=200)

    def post(self, request, comment_id):
        user_id = request.data.get('user_id', None)
        comment = Comment.objects.get(id=comment_id)
        user = User.objects.get(id=user_id)
        like = CommentLikes.objects.create(comment=comment, user=user)
        return Response({"message": "Like added successfully"}, status=201)

    def delete(self, request, comment_id):
        user_id = request.data.get('user_id', None)
        comment = Comment.objects.get(id=comment_id)
        user = User.objects.get(id=user_id)
        try:
            like = CommentLikes.objects.get(comment=comment, user=user)
            like.delete()
            return HttpResponse(status=204)
        except CommentLikes.DoesNotExist:
            return HttpResponse(status=404)
            
