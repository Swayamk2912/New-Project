from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Proposal
from .serializers import ProposalSerializer
from jobs.models import Job
from contracts.models import Contract
from messaging.models import Conversation
from payments.models import Payment

# 1️⃣ Create Proposal
from rest_framework.decorators import action

from rest_framework.views import APIView

class ProposalCreateView(generics.CreateAPIView):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(freelancer=self.request.user)


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


# 4️⃣ Accept Proposal
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def accept_proposal(request, pk):
    try:
        proposal = Proposal.objects.get(pk=pk)
    except Proposal.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)

    job = proposal.job
    if job.client != request.user:
        return Response({'detail': 'Not allowed'}, status=403)

    proposal.status = 'accepted'
    proposal.save()

    # Create contract
    contract = Contract.objects.create(
        job=job,
        client=job.client,
        freelancer=proposal.freelancer,
        agreed_budget=proposal.proposed_budget
    )

    # Create conversation
    conv = Conversation.objects.create()
    conv.participants.add(job.client, proposal.freelancer)

    # Mock payment
    Payment.objects.create(
        contract=contract,
        amount=proposal.proposed_budget,
        status='success',
        provider='mock'
    )

    return Response({'detail': 'Proposal accepted', 'contract_id': contract.id})


# 5️⃣ Reject Proposal
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reject_proposal(request, pk):
    try:
        proposal = Proposal.objects.get(pk=pk)
    except Proposal.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)

    job = proposal.job
    if job.client != request.user:
        return Response({'detail': 'Not allowed'}, status=403)

    proposal.status = 'rejected'
    proposal.save()

    return Response({'detail': 'Proposal rejected'})
