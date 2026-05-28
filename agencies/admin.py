from django.contrib import admin
from .models import Agency, AgencyLandlord

@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone_number', 'is_verified', 'commission_rate', 'created_at']
    list_filter = ['is_verified']
    search_fields = ['name', 'email', 'registration_number']

@admin.register(AgencyLandlord)
class AgencyLandlordAdmin(admin.ModelAdmin):
    list_display = ['agency', 'landlord', 'status', 'management_fee_percent', 'joined_at']
    list_filter = ['status']