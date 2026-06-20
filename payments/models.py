from django.db import models
from django.contrib.auth.models import User
from properties.models import Property, Lease
from agencies.models import Agency


class RentPayment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('MPESA', 'M-Pesa'),
        ('STRIPE', 'Stripe'),
        ('CASH', 'Cash'),
    ]

    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rent_payments')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='payments')
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='payments')
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='payments')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    nest_commission = models.DecimalField(max_digits=10, decimal_places=2)
    agency_earnings = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=200, unique=True, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_for_month = models.DateField()

    def save(self, *args, **kwargs):
        # Auto calculate NEST commission and agency earnings
        self.nest_commission = self.total_amount * (self.agency.commission_rate / 100)
        self.agency_earnings = self.total_amount - self.nest_commission
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tenant.email} — KSh {self.total_amount} ({self.status})"


class Payout(models.Model):
    TYPE_CHOICES = [
        ('AGENCY', 'Agency Payout'),
        ('LANDLORD', 'Landlord Payout'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSED', 'Processed'),
        ('FAILED', 'Failed'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payouts')
    payout_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    month = models.DateField()
    processed_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payout_type} — {self.recipient.email} — KSh {self.amount} ({self.status})"


class TenantCreditScore(models.Model):
    tenant = models.OneToOneField(User, on_delete=models.CASCADE, related_name='credit_score')
    score = models.PositiveIntegerField(default=100)
    total_payments = models.PositiveIntegerField(default=0)
    on_time_payments = models.PositiveIntegerField(default=0)
    late_payments = models.PositiveIntegerField(default=0)
    missed_payments = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tenant.email} — Score: {self.score}"
    
class Invoice(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    ]

    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='invoices')
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='invoices')
    title = models.CharField(max_length=200)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    due_date = models.DateField()
    ai_summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} — {self.tenant.email} ({self.status})"

    class Meta:
        ordering = ['-created_at']


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} — KSh {self.amount}"