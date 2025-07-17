from django.urls import path

from .views import CallSessionGetView, CallSessionPostView

urlpatterns = [
    path('session/<int:session_id>/', CallSessionGetView.as_view(), name='call_session_get'),
    path('session/', CallSessionPostView.as_view(), name='call_session_post'),
]
