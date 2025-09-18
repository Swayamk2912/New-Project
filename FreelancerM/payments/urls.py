from django.urls import path
from . import views

urlpatterns = [
    path("pay/<int:proposal_id>/", views.initiate_payment, name="payment"),
    path("success/", views.payment_success, name="payment_success"),
    path("api/pay/<int:proposal_id>/", views.PaymentView.as_view(), name="api_payment"),
]
