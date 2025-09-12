# proposals/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.ProposalCreateView.as_view(), name='proposal_create'),  # ✅ Class-based view
    path('my/', views.MyProposalsView.as_view(), name='my_proposals'),             # ✅ Class-based view
    path('<int:pk>/', views.ProposalDetailView.as_view(), name='proposal_detail'),  # ✅ Class-based view
    path('<int:pk>/accept/', views.accept_proposal, name='proposal_accept'),       # ✅ Function-based view
    path('<int:pk>/reject/', views.reject_proposal, name='proposal_reject'),       # ✅ Function-based view
]
