from django.urls import path
from .views import ChatView, ChatSessionGetView, ChatSessionPostView, ChatSessionPutView

urlpatterns = [
    path('users/<int:user_id>/sessions/', ChatView.as_view(), name='chat_list'),  # GET: 유저의 세션 리스트
    path('sessions/', ChatSessionPostView.as_view(), name='chat_session'),  # POST: 세션 메시지 추가
    path('sessions/<int:session_id>/', ChatSessionGetView.as_view(), name='chat_session'),  # POST: 세션 메시지 추가
    path('sessions/<int:session_id>/<int:order>/', ChatSessionPutView.as_view(), name='chat_session_update'),  # PUT: 세션 업데이트

]