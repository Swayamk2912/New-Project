from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("proposal", "amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("proposal__job__title", "proposal__freelancer__username")
