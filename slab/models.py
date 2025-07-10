from django.db import models
from user.models import UserProfile as User

# Create your models here.

class Slab(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    user = models.ManyToManyField(User, related_name='slabs', blank=True)
    # ManyToManyField는 다대다 관계를 나타내며, 여러 사용자가 여러 슬랩에 참여할 수 있게 한다. 
    # ManyToManyField는 중간 테이블을 자동으로 생성하여 관계를 관리한다. 즉 다대다 관계에서 하나의 모델에만 필드를 정의한다면, 상호 참조가 가능하다.
    # user_instance.slabs.all() : 사용자가 참여한 모든 슬랩을 가져온다.
    # slab_instance.user.all() : 슬랩에 참여한 모든 사용자를 가져온다.
    imoji = models.ImageField(upload_to='slab_imoji/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Post(models.Model):
    slab = models.ForeignKey(Slab, on_delete=models.CASCADE, related_name='posts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    views = 

class Answer(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class PostLikes(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='postlikes')
    created_at = models.DateTimeField(auto_now_add=True)

class AnswerLikes(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answerlikes')
    created_at = models.DateTimeField(auto_now_add=True)

class CommentLikes(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commentlikes')
    created_at = models.DateTimeField(auto_now_add=True)







# blank = True는 폼에서 필수 입력이 아니게 하고, null = True는 데이터베이스에서 NULL 값을 허용합니다.
# on_delete=models.CASCADE는 Slab이 삭제될 때 관련된 Post도 함께 삭제되도록 합니다.

