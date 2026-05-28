from django.contrib import admin
from .models import MaintenanceTicket, TicketComment

@admin.register(MaintenanceTicket)
class MaintenanceTicketAdmin(admin.ModelAdmin):
    list_display = ['title', 'property', 'reported_by', 'priority', 'status', 'created_at']
    list_filter = ['priority', 'status']
    search_fields = ['title', 'reported_by__email']

@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'author', 'created_at']
    search_fields = ['author__email']