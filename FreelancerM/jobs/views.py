from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets, permissions
from .models import Job
from .serializers import JobPostingSerializer
from .forms import JobForm
from proposals.forms import ProposalForm
from proposals.tasks import send_proposal_notification_email_task

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
            return redirect('home')  # Redirect to home page
    else:
        form = JobForm()
    return render(request, 'jobs/post_job.html', {'form': form})

def job_list(request):
    jobs = Job.objects.all().order_by('-created_at')
    return render(request, 'jobs/job_list.html', {'jobs': jobs})

@login_required
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    
    if request.user.role == 'freelancer' and request.user != job.client:
        if request.method == 'POST':
            form = ProposalForm(request.POST)
            if form.is_valid():
                proposal = form.save(commit=False)
                proposal.job = job
                proposal.freelancer = request.user
                proposal.save()
                print(f"New proposal added via HTML form: Proposal ID - {proposal.id}, Job - {proposal.job.title}, Freelancer - {proposal.freelancer.username}")
                send_proposal_notification_email_task.delay(proposal.id)
                messages.success(request, 'Your proposal has been submitted successfully!')
                return redirect('jobs:job-detail', pk=job.pk)
        else:
            form = ProposalForm()
    else:
        form = None # Or an empty form if you want to display it but disable submission

    context = {
        'job': job,
        'form': form,
    }
    return render(request, 'jobs/job_detail.html', context)
