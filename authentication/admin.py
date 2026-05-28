from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone_number', 'is_2fa_enabled', 'created_at']
    list_filter = ['role', 'is_2fa_enabled']
    search_fields = ['user__email']