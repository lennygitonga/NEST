from django.contrib import admin
from .models import RentPayment, Payout, TenantCreditScore
from .models import Invoice, InvoiceItem

@admin.register(RentPayment)
class RentPaymentAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'property', 'total_amount', 'nest_commission', 'agency_earnings', 'payment_method', 'status', 'payment_date']
    list_filter = ['status', 'payment_method']
    search_fields = ['tenant__email', 'transaction_id']

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'payout_type', 'amount', 'status', 'month', 'processed_at']
    list_filter = ['payout_type', 'status']
    search_fields = ['recipient__email']

@admin.register(TenantCreditScore)
class TenantCreditScoreAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'score', 'total_payments', 'on_time_payments', 'late_payments', 'missed_payments', 'last_updated']
    search_fields = ['tenant__email']



@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'tenant', 'agency', 'total_amount', 'status', 'due_date', 'created_at']
    list_filter = ['status']
    search_fields = ['tenant__email', 'title']


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'description', 'amount']