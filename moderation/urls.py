from django.urls import path
from . import views

urlpatterns = [
    # User moderation
    path('users/<int:user_id>/ban/', views.ban_user_view, name='ban_user'),
    path('users/<int:user_id>/unban/', views.unban_user_view, name='unban_user'),
    path('users/<int:user_id>/delete/', views.admin_delete_user_view, name='admin_delete_user'),
    path('users/<int:user_id>/warn/', views.issue_warning_view, name='issue_warning'),
    path('my-warnings/', views.my_warnings_view, name='my_warnings'),

    # Agency moderation
    path('agencies/<int:agency_id>/suspend/', views.suspend_agency_view, name='suspend_agency'),
    path('agencies/<int:agency_id>/unsuspend/', views.unsuspend_agency_view, name='unsuspend_agency'),
    path('agencies/<int:agency_id>/penalize/', views.penalize_agency_view, name='penalize_agency'),

    # Fraud reports
    path('fraud-reports/', views.list_fraud_reports_view, name='list_fraud_reports'),
    path('fraud-reports/file/', views.file_fraud_report_view, name='file_fraud_report'),
    path('fraud-reports/<int:report_id>/review/', views.review_fraud_report_view, name='review_fraud_report'),

    # Ban Appeals
    path('appeals/submit/', views.submit_ban_appeal_view, name='submit_ban_appeal'),
    path('appeals/', views.list_ban_appeals_view, name='list_ban_appeals'),
    path('appeals/<int:appeal_id>/review/', views.review_ban_appeal_view, name='review_ban_appeal'),

    # Audit log
    path('audit-log/', views.audit_log_view, name='audit_log'),
]