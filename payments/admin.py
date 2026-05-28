from django.contrib import admin
from .models import RentPayment, Payout, TenantCreditScore

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