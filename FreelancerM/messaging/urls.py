from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('start-conversation/<int:user_id>/', views.start_conversation, name='start_conversation'),
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),
    path('delete_conversation/<int:conversation_id>/', views.delete_conversation, name='delete_conversation'),
]
