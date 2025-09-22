from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('webhook/', views.notification_webhook, name='notification_webhook'),
    path('unread_count/', views.unread_notification_count, name='unread_notification_count'),
    path('list/api/', views.notification_list_api, name='notification_list_api'),
    path('list/', views.notification_list_page, name='notification_list'),
    path('mark_read/<int:notification_id>/', views.mark_single_notification_read, name='mark_single_notification_read'),
    path('mark_read/', views.mark_notifications_read, name='mark_notifications_read'),
]
