from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.home, name='home'),
    # App routes
    path("users/", include('users.urls',namespace='users')),
    path("jobs/", include("jobs.urls")),
    path("proposals/", include("proposals.urls")),
    #path("messages/", include("messaging.urls")),
    path("payments/", include("payments.urls")),
]
