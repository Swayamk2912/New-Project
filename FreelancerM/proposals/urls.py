# proposals/urls.py
from django.urls import path
from . import views

app_name = 'proposals'

urlpatterns = [
    path('submit/', views.ProposalCreateView.as_view(), name='proposal_create'),  # ✅ Class-based view
    path('my/', views.MyProposalsTemplateView.as_view(), name='my_proposals'), # Template view for freelancer's proposals
    path('<int:pk>/', views.proposal_detail_view, name='proposal_detail'),  # ✅ Function-based view
    path('jobs/', views.proposal_list_view, name='job_proposals'),         # Function-based view for client's job proposals
    path('<int:pk>/accept/', views.accept_proposal, name='proposal_accept'),       # ✅ Function-based view
    path('<int:pk>/reject/', views.reject_proposal, name='proposal_reject'),       # ✅ Function-based view
]
