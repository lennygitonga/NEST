from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.profile_view, name='profile'),
    path('password-reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password-reset-confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),
]