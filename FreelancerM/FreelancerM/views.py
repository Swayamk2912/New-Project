
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from jobs.models import Job
from users.models import Profile
from proposals.models import Proposal

def home(request):
    # Show homepage to everyone so stats are visible to all roles
    latest_jobs = Job.objects.order_by('-created_at')[:10]
    top_freelancers = Profile.objects.filter(user__role='freelancer')[:8] # Fetch top 8 freelancers
    UserModel = get_user_model()
    total_projects = Job.objects.count()

    # Clients: prefer role-based count; fallback to distinct job clients
    total_clients = UserModel.objects.filter(role='client').count()
    if total_clients == 0:
        total_clients = Job.objects.values('client_id').distinct().count()

    # Freelancers: prefer role-based count; fallback to distinct proposal freelancers, then profiles
    total_freelancers = UserModel.objects.filter(role='freelancer').count()
    if total_freelancers == 0:
        total_freelancers = Proposal.objects.values('freelancer_id').distinct().count()
    if total_freelancers == 0:
        total_freelancers = Profile.objects.filter(user__isnull=False).count()
    context = {
        'jobs': latest_jobs,
        'freelancers': top_freelancers,
        'total_clients': total_clients,
        'total_freelancers': total_freelancers,
        'total_projects': total_projects,
    }
    return render(request, 'home.html', context)
