from rest_framework import generics, permissions
from .models import Job
from .serializers import JobSerializer
from django.shortcuts import render


# List all jobs
class JobList(generics.ListAPIView):
    queryset = Job.objects.all().order_by('-created_at')
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]

# Post a job
class JobCreate(generics.CreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)
class JobDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        # Ensure only the client who posted the job can update
        if self.request.user != serializer.instance.client:
            raise PermissionError("You do not have permission to edit this job.")
        serializer.save()

    def perform_destroy(self, instance):
        # Ensure only the client who posted the job can delete
        if self.request.user != instance.client:
            raise PermissionError("You do not have permission to delete this job.")
        instance.delete()
        
        
def search(request):
    query = request.GET.get('q', '')
    jobs = Job.objects.all()
    if query:
        jobs = jobs.filter(title__icontains=query) | jobs.filter(description__icontains=query)
    return render(request, 'jobs/search_results.html', {'jobs': jobs, 'query': query})