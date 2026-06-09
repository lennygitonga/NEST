from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_list_create_view, name='payment_list_create'),
    path('<int:pk>/', views.payment_detail_view, name='payment_detail'),
    path('payouts/', views.payout_list_view, name='payout_list'),
    path('reports/monthly/', views.monthly_report_view, name='monthly_report'),
    path('credit-score/<int:tenant_id>/', views.tenant_credit_score_view, name='tenant_credit_score'),
]