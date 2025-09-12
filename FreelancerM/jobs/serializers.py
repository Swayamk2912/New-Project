from rest_framework import serializers
from .models import Job

class JobPostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'client', 'title', 'description', 'budget', 'deadline', 'created_at']
        read_only_fields = ['client', 'created_at']
