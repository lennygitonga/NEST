from django.db import models
from django.contrib.auth.models import User
from agencies.models import Agency


class AdminActionLog(models.Model):
    ACTION_CHOICES = [
        ('BAN_USER', 'Banned User'),
        ('UNBAN_USER', 'Unbanned User'),
        ('SUSPEND_AGENCY', 'Suspended Agency'),
        ('UNSUSPEND_AGENCY', 'Unsuspended Agency'),
        ('DELETE_USER', 'Deleted User'),
        ('WARN_USER', 'Issued Warning'),
        ('PENALIZE_AGENCY', 'Penalized Agency'),
        ('VERIFY_AGENCY', 'Verified Agency'),
    ]

    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='admin_actions')
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderation_actions_received')
    target_agency = models.ForeignKey(Agency, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderation_actions_received')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = self.target_user.email if self.target_user else (self.target_agency.name if self.target_agency else 'Unknown')
        return f"{self.action_type} — {target}"

    class Meta:
        ordering = ['-created_at']


class Warning(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='warnings')
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='warnings_issued')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Warning for {self.user.email}"

    class Meta:
        ordering = ['-created_at']


class FraudReport(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('REVIEWED', 'Reviewed'),
        ('DISMISSED', 'Dismissed'),
        ('ACTION_TAKEN', 'Action Taken'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fraud_reports_filed')
    reported_agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='fraud_reports')
    reason = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Report against {self.reported_agency.name} — {self.status}"

    class Meta:
        ordering = ['-created_at']


class BanAppeal(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved — Unbanned'),
        ('DISMISSED', 'Dismissed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ban_appeals')
    message = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    admin_response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Appeal by {self.user.email} — {self.status}"

    class Meta:
        ordering = ['-created_at']