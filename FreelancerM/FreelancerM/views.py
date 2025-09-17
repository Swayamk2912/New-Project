
from django.shortcuts import render, redirect
from jobs.models import Job
from users.models import Profile

def home(request):
    if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'freelancer':
        return redirect('jobs:job-list')
    latest_jobs = Job.objects.order_by('-created_at')[:10]
    top_freelancers = Profile.objects.filter(user__role='freelancer')[:8] # Fetch top 8 freelancers
    context = {
        'jobs': latest_jobs,
        'freelancers': top_freelancers,
    }
    return render(request, 'home.html', context)
