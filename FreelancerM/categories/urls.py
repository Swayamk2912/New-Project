from django.urls import path
from . import views

urlpatterns = [
    path('create-category/', views.create_category, name='create_category'),
    path('create-listing/', views.create_listing, name='create_listing'),
    path('category/<int:category_id>/', views.category_listings, name='category_listings'),
]
