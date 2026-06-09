from django.urls import path
from . import views

urlpatterns = [
    # Properties
    path('', views.property_list_view, name='property_list'),
    path('create/', views.property_create_view, name='property_create'),
    path('<int:pk>/', views.property_detail_view, name='property_detail'),
    path('<int:pk>/update/', views.property_update_view, name='property_update'),
    path('<int:pk>/delete/', views.property_delete_view, name='property_delete'),
    path('<int:pk>/images/', views.property_image_upload_view, name='property_image_upload'),
    path('<int:pk>/documents/', views.property_document_upload_view, name='property_document_upload'),

    # Applications
    path('applications/', views.application_list_create_view, name='application_list_create'),
    path('applications/<int:pk>/review/', views.application_review_view, name='application_review'),

    # Leases
    path('leases/', views.lease_list_create_view, name='lease_list_create'),
    path('leases/<int:pk>/', views.lease_detail_view, name='lease_detail'),
]