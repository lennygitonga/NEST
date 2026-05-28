from django.db import models
from django.contrib.auth.models import User


class Agency(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agency')
    name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='agency_logos/', blank=True, null=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Agencies'


class AgencyLandlord(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('TERMINATED', 'Terminated'),
    ]

    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='landlords')
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agency_relationships')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    management_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.agency.name} — {self.landlord.email}"

    class Meta:
        unique_together = ('agency', 'landlord')