from django.urls import path
from .views import register_view, login_view, logout_view
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('freelancers/', views.freelancer_list, name='freelancer_list'),
    path("password-reset/", views.password_reset_request, name="password_reset_request"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
    path('profile/', views.profile_view, name='profile'),
]
