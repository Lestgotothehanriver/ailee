from django.urls import path
from .views import UserSlabView, SlabPostView, PostDetailView, PostAnswerView, AnswerDetailView, AnswerCommentView, CommentDetailView, PostLikesView, AnswerLikesView, CommentLikesView

urlpatterns = [
    path('users/<int:user_id>/', UserSlabView.as_view(), name = 'user_slab'),
    path('<int:slab_id>/posts/', SlabPostView.as_view(), name='slab_posts'),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:post_id>/answers/', PostAnswerView.as_view(), name='post_answers'),
    path('answers/<int:answer_id>/', AnswerDetailView.as_view(), name='answer_detail'),
    path('answers/<int:answer_id>/comments/', AnswerCommentView.as_view(), name='answer_comments'),
    path('comments/<int:comment_id>/', CommentDetailView.as_view(), name='comment_detail'),
    path('posts/<int:post_id>/likes/', PostLikesView.as_view(), name='post_likes'),
    path('answers/<int:answer_id>/likes/', AnswerLikesView.as_view(), name='answer_likes'),
    path('comments/<int:comment_id>/likes/', CommentLikesView.as_view(), name='comment_likes'),
]

