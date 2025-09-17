from django.core.management.base import BaseCommand
from users.models import User, Profile

class Command(BaseCommand):
    help = 'Creates missing user profiles for existing users.'

    def handle(self, *args, **kwargs):
        users_without_profile = User.objects.filter(profile__isnull=True)
        count = 0
        for user in users_without_profile:
            Profile.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Created profile for user: {user.username}'))
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} missing profiles.'))
