from django.urls import path
from .views import post_job, job_list, job_detail

app_name = 'jobs'  # namespace for template reverse

urlpatterns = [
    path('post/', post_job, name='post_job'),
    path('', job_list, name='job-list'),
    path('<int:pk>/', job_detail, name='job-detail'),
]
