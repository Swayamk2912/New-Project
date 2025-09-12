from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "budget", "deadline", "created_at")
    search_fields = ("title", "description", "client__username")
    list_filter = ("deadline", "created_at")
