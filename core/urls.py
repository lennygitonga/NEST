from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

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

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)