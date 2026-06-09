from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list_view, name='notification_list'),
    path('<int:pk>/', views.notification_mark_read_view, name='notification_mark_read'),
    path('mark-all-read/', views.notification_mark_all_read_view, name='notification_mark_all_read'),
    path('<int:pk>/delete/', views.notification_delete_view, name='notification_delete'),
]