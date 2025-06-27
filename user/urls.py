from django.urls import path
from .views import UserCreateView, UserProfileView, UserLoginView

urlpatterns = [
    path('create/', UserCreateView.as_view(), name='user_create'),  # 사용자 프로필 생성
    path('user/<int:user_id>/', UserProfileView.as_view(), name='user_profile'),  # 사용자 프로필 조회 및 수정
    path('login/', UserLoginView.as_view(), name='user_login'),  # 사용자 로그인
]
