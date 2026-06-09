from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.agency_register_view, name='agency_register'),
    path('', views.agency_list_view, name='agency_list'),
    path('<int:pk>/verify/', views.agency_verify_view, name='agency_verify'),
    path('dashboard/', views.agency_dashboard_view, name='agency_dashboard'),
    path('landlords/', views.landlord_list_view, name='landlord_list'),
    path('landlords/add/', views.add_landlord_view, name='add_landlord'),
]