from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions
from .models import Job
from .serializers import JobPostingSerializer
from .forms import JobForm

class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by('-created_at')
    serializer_class = JobPostingSerializer

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

@login_required
def post_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.client = request.user
            job.save()
            return redirect('jobs:job-list')  # Redirect to job list or job detail page
    else:
        form = JobForm()
    return render(request, 'jobs/post_job.html', {'form': form})
