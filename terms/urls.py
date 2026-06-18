from django.urls import path
from . import views

urlpatterns = [
    path('current/', views.current_terms_view, name='current_terms'),
    path('', views.list_terms_view, name='list_terms'),
    path('create/', views.create_terms_view, name='create_terms'),
    path('accept/', views.accept_terms_view, name='accept_terms'),
    path('acceptance-status/', views.terms_acceptance_status_view, name='terms_acceptance_status'),
]