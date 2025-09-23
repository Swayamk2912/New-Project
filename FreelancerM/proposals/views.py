from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from notifications.models import Notification
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Proposal
from .serializers import ProposalSerializer
from jobs.models import Job
from contracts.models import Contract
from messaging.models import Conversation
from payments.models import Payment
from .tasks import send_proposal_notification_email_task # Import the Celery task

# 1️⃣ Create Proposal
from rest_framework.decorators import action

from rest_framework.views import APIView
from django.views.generic import TemplateView

@login_required
def proposal_list_view(request):
    proposals = Proposal.objects.filter(job__client=request.user).order_by('-created_at')
    context = {
        'proposals': proposals
    }
    return render(request, 'proposals/proposal_list.html', context)

class MyProposalsTemplateView(TemplateView):
    template_name = 'proposals/my_proposals.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated and self.request.user.role == 'freelancer':
            context['proposals'] = Proposal.objects.filter(freelancer=self.request.user).order_by('-created_at')
        else:
            context['proposals'] = Proposal.objects.none() # Or handle unauthorized access
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'freelancer':
            messages.error(request, "You are not authorized to view this page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

@login_required
def proposal_detail_view(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)
    # Ensure only the freelancer who made the proposal or the client who owns the job can view it
    if request.user != proposal.freelancer and request.user != proposal.job.client:
        messages.error(request, "You are not authorized to view this proposal.")
        return redirect('home') # Redirect to home or a more appropriate page

    context = {
        'proposal': proposal
    }
    return render(request, 'proposals/proposal_detail.html', context)

class ProposalCreateView(generics.CreateAPIView):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        print("vffffffffffffffffffffffffffffffffffffffffffffff")
        proposal = serializer.save(freelancer=self.request.user)
        print(f"New proposal added to the table: Proposal ID - {proposal.id}, Job - {proposal.job.title}, Freelancer - {proposal.freelancer.username}")
        # Send email notification to the client asynchronously using Celery
        send_proposal_notification_email_task.delay(proposal.id)


proposal_create = ProposalCreateView.as_view()


# 2️⃣ List My Proposals
class MyProposalsView(generics.ListAPIView):
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Proposal.objects.filter(freelancer=self.request.user).order_by('-created_at')


# 3️⃣ Proposal Detail
class ProposalDetailView(generics.RetrieveAPIView):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]


# 4️⃣ List Proposals for Client's Jobs
class JobProposalsView(generics.ListAPIView):
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter proposals for jobs posted by the current client
        return Proposal.objects.filter(job__client=self.request.user).order_by('-created_at')


# 5️⃣ Accept Proposal
@login_required
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def accept_proposal(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)

    job = proposal.job
    if job.client != request.user:
        messages.error(request, "You are not authorized to accept this proposal.")
        return redirect('proposals:proposal_detail', pk=pk)

    if proposal.status == 'pending':
        proposal.status = 'accepted'
        proposal.save()

        # Create notification for the freelancer
        notification_message = f"Your proposal for '{job.title}' has been accepted!"
        Notification.objects.create(
            user=proposal.freelancer,
            verb=notification_message,
            payload={'proposal_id': proposal.id, 'job_id': job.id, 'status': 'accepted'}
        )

        # Send real-time notification via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{proposal.freelancer.id}",
            {
                "type": "send_notification",
                "message": {
                    "action": "new_notification",
                    "title": "Proposal Accepted",
                    "message": notification_message,
                    "url": f"/proposals/{proposal.id}/",
                    "timestamp": str(Notification.objects.filter(user=proposal.freelancer).latest('created_at').created_at)
                },
            }
        )

        # Create contract
        contract = Contract.objects.create(
            job=job,
            client=job.client,
            freelancer=proposal.freelancer,
            agreed_budget=proposal.budget
        )

        # Create conversation
        conv = Conversation.objects.create()
        conv.participants.add(job.client, proposal.freelancer)

        messages.success(request, "Proposal accepted successfully and contract created.")
    else:
        messages.warning(request, f"Proposal is already {proposal.status}.")

    return redirect('proposals:proposal_detail', pk=pk)


# 5️⃣ Reject Proposal
@login_required
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reject_proposal(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)

    job = proposal.job
    if job.client != request.user:
        messages.error(request, "You are not authorized to reject this proposal.")
        return redirect('proposals:proposal_detail', pk=pk)

    if proposal.status == 'pending':
        proposal.status = 'rejected'
        proposal.save()
        messages.success(request, "Proposal rejected successfully.")

        # Create notification for the freelancer
        notification_message = f"Your proposal for '{job.title}' has been rejected."
        Notification.objects.create(
            user=proposal.freelancer,
            verb=notification_message,
            payload={'proposal_id': proposal.id, 'job_id': job.id, 'status': 'rejected'}
        )

        # Send real-time notification via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{proposal.freelancer.id}",
            {
                "type": "send_notification",
                "message": {
                    "action": "new_notification",
                    "title": "Proposal Rejected",
                    "message": notification_message,
                    "url": f"/proposals/{proposal.id}/",
                    "timestamp": str(Notification.objects.filter(user=proposal.freelancer).latest('created_at').created_at)
                },
            }
        )
    else:
        messages.warning(request, f"Proposal is already {proposal.status}.")

    return redirect('proposals:proposal_detail', pk=pk)
