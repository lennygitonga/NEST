from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Registration & Login
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.profile_view, name='profile'),

    # Email Verification
    path('verify-email/', views.verify_email_view, name='verify_email'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),

    # Password Reset
    path('password-reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password-reset-confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),

    # 2FA
    path('2fa/setup/', views.setup_2fa_view, name='2fa_setup'),
    path('2fa/verify-setup/', views.verify_2fa_setup_view, name='2fa_verify_setup'),
    path('2fa/verify-login/', views.verify_2fa_login_view, name='2fa_verify_login'),
    path('2fa/disable/', views.disable_2fa_view, name='2fa_disable'),
]