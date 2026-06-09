from django.urls import path
from . import views

urlpatterns = [
    path('', views.ticket_list_create_view, name='ticket_list_create'),
    path('<int:pk>/', views.ticket_detail_view, name='ticket_detail'),
    path('<int:pk>/status/', views.ticket_status_update_view, name='ticket_status_update'),
    path('<int:pk>/comments/', views.ticket_comment_list_create_view, name='ticket_comment_list_create'),
]