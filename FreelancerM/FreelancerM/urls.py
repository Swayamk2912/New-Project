from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('marketplace/', include('marketplace.urls')),
    path('users/', include('users.urls')),
    path('jobs/', include('jobs.urls')),
    path('categories/', include('categories.urls')),
    path('proposals/', include('proposals.urls')),
    path('messages/', include('messaging.urls')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('api/users/', include('users.api_urls')),
    path('api/jobs/', include('jobs.api_urls')),
    path('notifications/', include('notifications.urls')), # Include notifications app URLs
    path('accounts/', include('allauth.urls')),
]
