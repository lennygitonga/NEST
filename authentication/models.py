from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('NEST_ADMIN', 'Nest Admin'),
        ('AGENCY', 'Agency'),
        ('LANDLORD', 'Landlord'),
        ('TENANT', 'Tenant'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    id_document = models.FileField(upload_to='id_documents/', blank=True, null=True)
    is_2fa_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=32, blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=6, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(blank=True, null=True)
    deletion_requested_at = models.DateTimeField(blank=True, null=True)
    is_pending_deletion = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} — {self.role}"

    def is_nest_admin(self):
        return self.role == 'NEST_ADMIN'

    def is_agency(self):
        return self.role == 'AGENCY'

    def is_landlord(self):
        return self.role == 'LANDLORD'

    def is_tenant(self):
        return self.role == 'TENANT'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, role='TENANT')


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()