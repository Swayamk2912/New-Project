from django.shortcuts import render
from django.contrib.auth import get_user_model
from jobs.models import Job
from users.models import Profile
from proposals.models import Proposal

def home(request):
    latest_jobs = Job.objects.order_by('-created_at')[:6]
    featured_freelancers = Profile.objects.filter(user__role='freelancer')[:4]

    UserModel = get_user_model()
    total_projects = Job.objects.count()

    total_clients = UserModel.objects.filter(role='client').count()
    if total_clients == 0:
        total_clients = Job.objects.values('client_id').distinct().count()

    total_freelancers = UserModel.objects.filter(role='freelancer').count()
    if total_freelancers == 0:
        total_freelancers = Proposal.objects.values('freelancer_id').distinct().count()
    if total_freelancers == 0:
        total_freelancers = Profile.objects.filter(user__isnull=False).count()

    context = {
        'jobs': latest_jobs,
        'freelancers': featured_freelancers,
        'total_projects': total_projects,
        'total_clients': total_clients,
        'total_freelancers': total_freelancers,
    }
    return render(request, 'home.html', context)
    