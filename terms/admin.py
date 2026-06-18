from django.contrib import admin
from .models import TermsAndConditions, UserTermsAcceptance


@admin.register(TermsAndConditions)
class TermsAndConditionsAdmin(admin.ModelAdmin):
    list_display = ['version', 'title', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['version', 'title']


@admin.register(UserTermsAcceptance)
class UserTermsAcceptanceAdmin(admin.ModelAdmin):
    list_display = ['user', 'terms', 'accepted_at']
    search_fields = ['user__email']
    list_filter = ['terms']