from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_list_create_view, name='payment_list_create'),
    path('<int:pk>/', views.payment_detail_view, name='payment_detail'),
    path('<int:pk>/receipt/', views.payment_receipt_view, name='payment_receipt'),
    path('<int:pk>/receipt/download/', views.payment_receipt_download_view, name='payment_receipt_download'),
    path('my-statement/', views.my_statement_view, name='my_statement'),
    path('payouts/', views.payout_list_view, name='payout_list'),
    path('reports/monthly/', views.monthly_report_view, name='monthly_report'),
    path('credit-score/<int:tenant_id>/', views.tenant_credit_score_view, name='tenant_credit_score'),
]