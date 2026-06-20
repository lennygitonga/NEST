from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Schema & Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Authentication
    path('api/auth/', include('authentication.urls')),

    # Google OAuth
    path('api/auth/social/', include('dj_rest_auth.urls')),
    path('api/auth/social/registration/', include('dj_rest_auth.registration.urls')),
    path('api/auth/social/google/', include('allauth.socialaccount.urls')),

    # Agencies
    path('api/agencies/', include('agencies.urls')),

    # Properties
    path('api/properties/', include('properties.urls')),

    # Tickets
    path('api/tickets/', include('tickets.urls')),

    # Payments
    path('api/payments/', include('payments.urls')),

    # Notifications
    path('api/notifications/', include('notifications.urls')),

    # Terms & Conditions
    path('api/terms/', include('terms.urls')),

    # Moderation
    path('api/moderation/', include('moderation.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)