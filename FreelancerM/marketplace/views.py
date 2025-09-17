from django.shortcuts import render
from jobs.models import Job
from users.models import Profile

def home(request):
    latest_jobs = Job.objects.order_by('-created_at')[:6]  # Get latest 6 jobs
    featured_freelancers = Profile.objects.filter(is_freelancer=True)[:4] # Get 4 featured freelancers
    context = {
        'jobs': latest_jobs,
        'freelancers': featured_freelancers,
    }
    return render(request, 'home.html', context)