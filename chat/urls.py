from django.urls import path
from .views import ChatView, ChatSessionView

urlpatterns = [
    path('users/<int:user_id>/sessions/', ChatView.as_view(), name='chat_list'),  # GET: 유저의 세션 리스트
    path('sessions/<int:session_id>/', ChatSessionView.as_view(), name='chat_session'),  # GET/POST: 세션 메시지 조회/추가
]