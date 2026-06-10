from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Makes an existing user a superuser'

    def handle(self, *args, **kwargs):
        try:
            u = User.objects.get(email='admin@nest.com')
            u.is_staff = True
            u.is_superuser = True
            u.save()
            self.stdout.write('Successfully made admin@nest.com a superuser')
        except User.DoesNotExist:
            self.stdout.write('User not found')