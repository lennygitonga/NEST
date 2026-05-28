from django.contrib import admin
from .models import Property, PropertyImage, PropertyDocument, PropertyApplication, Lease

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'agency', 'landlord', 'property_type', 'city', 'rent_amount', 'is_vacant', 'is_published']
    list_filter = ['property_type', 'is_vacant', 'is_published', 'city']
    search_fields = ['title', 'address', 'city']

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ['property', 'uploaded_at']

@admin.register(PropertyDocument)
class PropertyDocumentAdmin(admin.ModelAdmin):
    list_display = ['property', 'label', 'uploaded_at']

@admin.register(PropertyApplication)
class PropertyApplicationAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'property', 'status', 'applied_at', 'reviewed_at']
    list_filter = ['status']
    search_fields = ['tenant__email']

@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'property', 'agency', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']
    search_fields = ['tenant__email']