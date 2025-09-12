from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from proposals.models import Proposal
from contracts.models import Contract
from .models import Payment

class PaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, proposal_id):
        try:
            # Get the proposal
            proposal = Proposal.objects.get(pk=proposal_id)
        except Proposal.DoesNotExist:
            return Response({'detail': 'Proposal not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is allowed to pay (the client)
        if proposal.job.client != request.user:
            return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)

        # Ensure proposal is accepted
        if proposal.status != 'accepted':
            return Response({'detail': 'Proposal is not accepted yet'}, status=status.HTTP_400_BAD_REQUEST)

        # Create contract if not already created
        contract, created = Contract.objects.get_or_create(
            job=proposal.job,
            client=proposal.job.client,
            freelancer=proposal.freelancer,
            agreed_budget=proposal.proposed_budget
        )

        # Create payment
        payment = Payment.objects.create(
            contract=contract,
            amount=proposal.proposed_budget,
            status='success',  # for now, we are mocking payment success
            provider='mock'
        )

        return Response({
            'detail': 'Payment successful',
            'payment_id': payment.id,
            'contract_id': contract.id
        }, status=status.HTTP_201_CREATED)

def payment_success(request):
    """
    Simple view to show a payment success page.
    """
    return render(request, "payments/success.html")