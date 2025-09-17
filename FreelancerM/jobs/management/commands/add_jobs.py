from django.core.management.base import BaseCommand
from jobs.models import Job
from users.models import User
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Adds some sample jobs to the database.'

    def handle(self, *args, **options):
        user = User.objects.filter(username='admin').first()
        if user:
            jobs = [
                {'title': 'Build a responsive website', 'description': 'We need a modern and responsive website for our startup.', 'budget': 1200.00, 'client': user, 'deadline': timezone.now().date() + timedelta(days=30)},
                {'title': 'Design a mobile app UI', 'description': 'Looking for a UI/UX designer to create a stunning mobile app interface.', 'budget': 800.00, 'client': user, 'deadline': timezone.now().date() + timedelta(days=20)},
                {'title': 'Write a technical blog post', 'description': 'We need a well-researched blog post on the topic of AI.', 'budget': 200.00, 'client': user, 'deadline': timezone.now().date() + timedelta(days=10)},
            ]
            for job_data in jobs:
                Job.objects.get_or_create(**job_data)
            self.stdout.write(self.style.SUCCESS('Successfully added sample jobs.'))
        else:
            self.stdout.write(self.style.ERROR('Admin user not found. Please create a superuser first.'))
