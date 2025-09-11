
from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "posted_by", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "posted_by__username")


