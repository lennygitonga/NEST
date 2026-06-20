from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from authentication.models import UserProfile


class Command(BaseCommand):
    help = 'Permanently deletes accounts that have passed their 7 day deletion grace period'

    def handle(self, *args, **kwargs):
        cutoff = timezone.now() - timedelta(days=7)
        expired_profiles = UserProfile.objects.filter(
            is_pending_deletion=True,
            deletion_requested_at__lte=cutoff
        )

        count = expired_profiles.count()

        for profile in expired_profiles:
            user_email = profile.user.email
            profile.user.delete()
            self.stdout.write(f'Permanently deleted: {user_email}')

        self.stdout.write(f'Total accounts deleted: {count}')