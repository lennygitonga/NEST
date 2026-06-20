from django.contrib import admin
from .models import AdminActionLog, Warning, FraudReport
from .models import BanAppeal


@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    list_display = ['action_type', 'admin', 'target_user', 'target_agency', 'created_at']
    list_filter = ['action_type']
    search_fields = ['admin__email', 'target_user__email', 'target_agency__name']


@admin.register(Warning)
class WarningAdmin(admin.ModelAdmin):
    list_display = ['user', 'issued_by', 'created_at']
    search_fields = ['user__email']


@admin.register(FraudReport)
class FraudReportAdmin(admin.ModelAdmin):
    list_display = ['reported_agency', 'reporter', 'status', 'created_at', 'reviewed_at']
    list_filter = ['status']
    search_fields = ['reported_agency__name', 'reporter__email']



@admin.register(BanAppeal)
class BanAppealAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'created_at', 'reviewed_at']
    list_filter = ['status']
    search_fields = ['user__email']