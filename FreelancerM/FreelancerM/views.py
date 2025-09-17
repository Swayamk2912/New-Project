
from django.shortcuts import render
from jobs.models import Job

def home(request):
    latest_jobs = Job.objects.order_by('-created_at')[:10]
    return render(request, 'home.html', {'jobs': latest_jobs})
