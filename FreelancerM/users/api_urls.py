from django.urls import path
from .views import RegisterUserAPI, LoginUserAPI

urlpatterns = [
    path('register/', RegisterUserAPI.as_view(), name='api-register'),
    path('login/', LoginUserAPI.as_view(), name='api-login'),
]
