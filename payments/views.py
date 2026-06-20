from rest_framework import status
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from core.ai_utils import ask_groq
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.utils import timezone
from .models import RentPayment, Payout, TenantCreditScore
from .serializers import (
    RentPaymentSerializer, PayoutSerializer,
    TenantCreditScoreSerializer, MonthlyReportSerializer
)


def is_agency(user):
    return user.profile.role == 'AGENCY'


def is_tenant(user):
    return user.profile.role == 'TENANT'


def is_landlord(user):
    return user.profile.role == 'LANDLORD'


def is_nest_admin(user):
    return user.profile.role == 'NEST_ADMIN'


def update_credit_score(tenant, on_time=True):
    credit_score, created = TenantCreditScore.objects.get_or_create(tenant=tenant)
    credit_score.total_payments += 1
    if on_time:
        credit_score.on_time_payments += 1
        credit_score.score = min(credit_score.score + 5, 100)
    else:
        credit_score.late_payments += 1
        credit_score.score = max(credit_score.score - 10, 0)
    credit_score.save()


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def payment_list_create_view(request):
    if request.method == 'GET':
        if is_agency(request.user):
            payments = RentPayment.objects.filter(agency=request.user.agency)
        elif is_tenant(request.user):
            payments = RentPayment.objects.filter(tenant=request.user)
        elif is_landlord(request.user):
            payments = RentPayment.objects.filter(property__landlord=request.user)
        elif is_nest_admin(request.user):
            payments = RentPayment.objects.all()
        else:
            return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = RentPaymentSerializer(payments, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        if not is_tenant(request.user):
            return Response({'error': 'Only tenants can make payments.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = RentPaymentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            payment = serializer.save()
            update_credit_score(request.user, on_time=True)
            return Response({
                'message': 'Payment recorded successfully.',
                'payment': RentPaymentSerializer(payment).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_detail_view(request, pk):
    if is_agency(request.user):
        payment = get_object_or_404(RentPayment, pk=pk, agency=request.user.agency)
    elif is_tenant(request.user):
        payment = get_object_or_404(RentPayment, pk=pk, tenant=request.user)
    elif is_landlord(request.user):
        payment = get_object_or_404(RentPayment, pk=pk, property__landlord=request.user)
    else:
        return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = RentPaymentSerializer(payment)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payout_list_view(request):
    if is_agency(request.user) or is_landlord(request.user):
        payouts = Payout.objects.filter(recipient=request.user)
    elif is_nest_admin(request.user):
        payouts = Payout.objects.all()
    else:
        return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = PayoutSerializer(payouts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_report_view(request):
    if not is_agency(request.user) and not is_landlord(request.user) and not is_nest_admin(request.user):
        return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)

    month = request.query_params.get('month')
    if not month:
        return Response({'error': 'Please provide a month parameter (YYYY-MM-DD).'}, status=status.HTTP_400_BAD_REQUEST)

    if is_agency(request.user):
        payments = RentPayment.objects.filter(
            agency=request.user.agency,
            payment_for_month__startswith=month[:7]
        )
    elif is_landlord(request.user):
        payments = RentPayment.objects.filter(
            property__landlord=request.user,
            payment_for_month__startswith=month[:7]
        )
    else:
        payments = RentPayment.objects.filter(
            payment_for_month__startswith=month[:7]
        )

    totals = payments.aggregate(
        total_collected=Sum('total_amount'),
        nest_commission=Sum('nest_commission'),
        agency_earnings=Sum('agency_earnings')
    )

    report = {
        'month': month,
        'total_collected': totals['total_collected'] or 0,
        'nest_commission': totals['nest_commission'] or 0,
        'agency_earnings': totals['agency_earnings'] or 0,
        'total_payments': payments.count()
    }

    serializer = MonthlyReportSerializer(report)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tenant_credit_score_view(request, tenant_id):
    if not is_agency(request.user):
        return Response({'error': 'Only agencies can view tenant credit scores.'}, status=status.HTTP_403_FORBIDDEN)
    credit_score = get_object_or_404(TenantCreditScore, tenant__id=tenant_id)
    serializer = TenantCreditScoreSerializer(credit_score)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_statement_view(request):
    if not is_tenant(request.user):
        return Response({'error': 'Only tenants can view their payment statement.'}, status=status.HTTP_403_FORBIDDEN)

    payments = RentPayment.objects.filter(tenant=request.user).order_by('-payment_date')

    total_paid = payments.filter(status='COMPLETED').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_payments_count = payments.filter(status='COMPLETED').count()

    return Response({
        'tenant': request.user.email,
        'total_paid': total_paid,
        'total_payments_count': total_payments_count,
        'payments': RentPaymentSerializer(payments, many=True).data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_receipt_view(request, pk):
    if is_agency(request.user):
        payment = get_object_or_404(RentPayment, pk=pk, agency=request.user.agency)
    elif is_tenant(request.user):
        payment = get_object_or_404(RentPayment, pk=pk, tenant=request.user)
    elif is_landlord(request.user):
        payment = get_object_or_404(RentPayment, pk=pk, property__landlord=request.user)
    else:
        return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)

    prompt = (
        f"Write a short, warm, professional one-sentence confirmation message for a rent payment receipt. "
        f"Tenant: {payment.tenant.first_name}. Amount: KSh {payment.total_amount}. "
        f"Property: {payment.property.title}. Keep it under 25 words."
    )
    confirmation_message = ask_groq(prompt, system_prompt="You write short professional receipt confirmation messages.")

    return Response({
        'receipt_number': f"NEST-RCT-{payment.id:06d}",
        'tenant_name': f"{payment.tenant.first_name} {payment.tenant.last_name}",
        'property': payment.property.title,
        'amount_paid': payment.total_amount,
        'payment_method': payment.payment_method,
        'transaction_id': payment.transaction_id,
        'payment_date': payment.payment_date,
        'payment_for_month': payment.payment_for_month,
        'status': payment.status,
        'confirmation_message': confirmation_message
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_receipt_download_view(request, pk):
    if is_agency(request.user):
        payment = get_object_or_404(RentPayment, pk=pk, agency=request.user.agency)
    elif is_tenant(request.user):
        payment = get_object_or_404(RentPayment, pk=pk, tenant=request.user)
    elif is_landlord(request.user):
        payment = get_object_or_404(RentPayment, pk=pk, property__landlord=request.user)
    else:
        return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="NEST_Receipt_{payment.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 20)
    p.drawString(2*cm, height - 2*cm, "NEST")

    p.setFont("Helvetica", 10)
    p.drawString(2*cm, height - 2.7*cm, "Real Estate Property Management Platform")

    p.line(2*cm, height - 3*cm, width - 2*cm, height - 3*cm)

    p.setFont("Helvetica-Bold", 14)
    p.drawString(2*cm, height - 4*cm, "PAYMENT RECEIPT")

    p.setFont("Helvetica", 11)
    y = height - 5*cm
    line_height = 0.7*cm

    details = [
        f"Receipt Number: NEST-RCT-{payment.id:06d}",
        f"Tenant Name: {payment.tenant.first_name} {payment.tenant.last_name}",
        f"Property: {payment.property.title}",
        f"Amount Paid: KSh {payment.total_amount}",
        f"Payment Method: {payment.payment_method}",
        f"Transaction ID: {payment.transaction_id or 'N/A'}",
        f"Payment Date: {payment.payment_date.strftime('%d %B %Y, %I:%M %p')}",
        f"Payment For Month: {payment.payment_for_month.strftime('%B %Y')}",
        f"Status: {payment.status}",
    ]

    for line in details:
        p.drawString(2*cm, y, line)
        y -= line_height

    p.line(2*cm, y - 0.3*cm, width - 2*cm, y - 0.3*cm)
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(2*cm, y - 1*cm, "This is a system generated receipt from NEST Property Management Platform.")

    p.showPage()
    p.save()

    return response