from rest_framework import viewsets, permissions
from .models import Job
from .serializers import JobPostingSerializer

class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by('-created_at')
    serializer_class = JobPostingSerializer

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)
