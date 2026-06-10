from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Creates or promotes a superuser'

    def handle(self, *args, **kwargs):
        email = 'admin@nest.com'
        password = 'NestAdmin2024'
        username = 'admin'

        if User.objects.filter(email=email).exists():
            u = User.objects.get(email=email)
            u.is_staff = True
            u.is_superuser = True
            u.set_password(password)
            u.save()
            self.stdout.write(f'Promoted {email} to superuser')
        else:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(f'Created superuser {email}')