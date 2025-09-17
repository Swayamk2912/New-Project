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
    path('dashboard/', views.freelancer_dashboard, name='freelancer_dashboard'),
    path('proposals-sent/', views.proposals_sent_view, name='proposals_sent'),
    path('freelancers/<int:pk>/', views.freelancer_detail, name='freelancer_detail'),
    path('client-dashboard/', views.client_dashboard, name='client_dashboard'),
]
