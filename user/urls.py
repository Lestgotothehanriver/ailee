from django.urls import path
from .views import UserCreateView, UserProfileView, UserLoginView, UserFollowView, UserFollowingView

urlpatterns = [
    path('create/', UserCreateView.as_view(), name='user_create'),  # 사용자 프로필 생성
    path('<int:user_id>/', UserProfileView.as_view(), name='user_profile'),  # 사용자 프로필 조회 및 수정
    path('<int:user_id>/follow/', UserFollowView.as_view(), name = 'user_follow'),  # 사용자 팔로우
    path('<int:user_id>/following/', UserFollowingView.as_view(), name='user_following'),  # 팔로우하는 사람들 조회
    path('<int:user_id>/followers/', UserFollowingView.as_view(), name='user_followers'),  # 팔로우를 받는 사람들 조회
    path('login/', UserLoginView.as_view(), name='user_login'),  # 사용자 로그인
]
