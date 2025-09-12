# contracts/models.py
from django.db import models
from django.conf import settings
from jobs.models import Job

class Contract(models.Model):
    STATUS = (('active','Active'),('completed','Completed'),('cancelled','Cancelled'))
    job = models.OneToOneField(Job, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_contracts')
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='freelancer_contracts')
    agreed_budget = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='active')
