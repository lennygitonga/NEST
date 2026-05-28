from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Notification(models.Model):
    TYPE_CHOICES = [
        ('LEASE_EXPIRY', 'Lease Expiry Warning'),
        ('PAYMENT_REMINDER', 'Payment Reminder'),
        ('PAYMENT_RECEIVED', 'Payment Received'),
        ('PAYOUT_PROCESSED', 'Payout Processed'),
        ('TICKET_UPDATE', 'Maintenance Ticket Update'),
        ('APPLICATION_UPDATE', 'Application Update'),
        ('AGENCY_VERIFIED', 'Agency Verified'),
        ('AGENCY_REJECTED', 'Agency Rejected'),
        ('GENERAL', 'General'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='GENERAL')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    # Generic link to any related object (ticket, payment, lease etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    linked_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_type} → {self.recipient.email}"

    class Meta:
        ordering = ['-created_at']
        