from django.urls import path
from .views import register_view, login_view, logout_view, select_role
from . import views

app_name = 'users'

urlpatterns = [
    path('select_role/', select_role, name='select_role'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('freelancers/', views.freelancer_list, name='freelancer_list'),
    path('freelancer/<int:pk>/', views.freelancer_detail, name='freelancer_detail'),
    path("password-reset/", views.password_reset_request, name="password_reset_request"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.freelancer_dashboard, name='freelancer_dashboard'),
    path('dashboard/client/', views.client_dashboard, name='client_dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path("password-reset/done/", views.password_reset_done, name="password_reset_done"),
    path("password-reset/complete/", views.password_reset_complete, name="password_reset_complete"),
]
