from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.home, name='dashboard'),
    # App routes
    path("users/", include('users.urls',namespace='users')),
    path("jobs/", include("jobs.urls", namespace='jobs')), # Template views
    path("api/jobs/", include("jobs.api_urls")), # API views
    path("proposals/", include("proposals.urls", namespace='proposals')),
    path("messages/", include("messaging.urls", namespace='messaging')),
    path("payments/", include("payments.urls")),
    # django-allauth urls
    path('accounts/', include('allauth.urls')),
]
