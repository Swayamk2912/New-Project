from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from users.views import RegisterUserAPI  # Only if you defined class RegisterUser


urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="user/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("register/", views.RegisterUserAPI.as_view(), name="register"),
    path("profile/", views.profile, name="profile"),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
