from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('webhook/', views.notification_webhook, name='notification_webhook'),
    path('unread_count/', views.unread_notification_count, name='unread_notification_count'),
    path('list/', views.notification_list, name='notification_list'),
    path('mark_read/', views.mark_notifications_read, name='mark_notifications_read'),
]
