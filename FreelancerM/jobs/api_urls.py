from django.urls import path
from .views import (
    JobList,
    JobCreate,
    JobDetail,
)

urlpatterns = [
    # List all jobs
    path('jobs/', JobList.as_view(), name='api-job-list'),

    # Create a new job
    path('jobs/create/', JobCreate.as_view(), name='api-job-create'),

    # Retrieve, update, or delete a specific job
    path('jobs/<int:pk>/', JobDetail.as_view(), name='api-job-detail'),
]
