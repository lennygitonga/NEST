from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from properties.models import Lease
from payments.models import TenantCreditScore
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Agency, AgencyLandlord
from .serializers import (
    AgencySerializer, AgencyRegisterSerializer,
    AgencyVerifySerializer, AgencyLandlordSerializer,
    AgencyDashboardSerializer
)


def is_nest_admin(user):
    return user.profile.role == 'NEST_ADMIN'


def is_agency(user):
    return user.profile.role == 'AGENCY'


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agency_register_view(request):
    if not is_agency(request.user):
        return Response({'error': 'Only agency accounts can register an agency.'}, status=status.HTTP_403_FORBIDDEN)
    if hasattr(request.user, 'agency'):
        return Response({'error': 'This user already has an agency registered.'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = AgencyRegisterSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        agency = serializer.save()
        return Response({
            'message': 'Agency registered successfully. Awaiting verification.',
            'agency': AgencySerializer(agency).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agency_list_view(request):
    if not is_nest_admin(request.user):
        return Response({'error': 'Only NEST admins can view all agencies.'}, status=status.HTTP_403_FORBIDDEN)
    agencies = Agency.objects.all()
    serializer = AgencySerializer(agencies, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def agency_verify_view(request, pk):
    if not is_nest_admin(request.user):
        return Response({'error': 'Only NEST admins can verify agencies.'}, status=status.HTTP_403_FORBIDDEN)
    agency = get_object_or_404(Agency, pk=pk)
    serializer = AgencyVerifySerializer(agency, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        status_text = 'verified' if agency.is_verified else 'rejected'
        return Response({'message': f'Agency {status_text} successfully.'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agency_dashboard_view(request):
    if not is_agency(request.user):
        return Response({'error': 'Only agencies can access this dashboard.'}, status=status.HTTP_403_FORBIDDEN)
    agency = get_object_or_404(Agency, user=request.user)
    serializer = AgencyDashboardSerializer(agency)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_landlord_view(request):
    if not is_agency(request.user):
        return Response({'error': 'Only agencies can add landlords.'}, status=status.HTTP_403_FORBIDDEN)
    agency = get_object_or_404(Agency, user=request.user)
    serializer = AgencyLandlordSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(agency=agency)
        return Response({
            'message': 'Landlord added successfully.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def landlord_list_view(request):
    if not is_agency(request.user):
        return Response({'error': 'Only agencies can view their landlords.'}, status=status.HTTP_403_FORBIDDEN)
    agency = get_object_or_404(Agency, user=request.user)
    landlords = AgencyLandlord.objects.filter(agency=agency)
    serializer = AgencyLandlordSerializer(landlords, many=True)
    return Response(serializer.data)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agency_tenants_view(request):
    if not is_agency(request.user):
        return Response({'error': 'Only agencies can view their tenants.'}, status=status.HTTP_403_FORBIDDEN)

    agency = get_object_or_404(Agency, user=request.user)
    leases = Lease.objects.filter(agency=agency, is_active=True).select_related('tenant', 'property')

    tenants_data = []
    for lease in leases:
        try:
            credit_score = TenantCreditScore.objects.get(tenant=lease.tenant)
            score = credit_score.score
        except TenantCreditScore.DoesNotExist:
            score = 100

        tenants_data.append({
            'tenant_id': lease.tenant.id,
            'tenant_name': f"{lease.tenant.first_name} {lease.tenant.last_name}",
            'tenant_email': lease.tenant.email,
            'property': lease.property.title,
            'property_id': lease.property.id,
            'lease_start_date': lease.start_date,
            'lease_end_date': lease.end_date,
            'rent_amount': lease.rent_amount,
            'credit_score': score
        })

    return Response({
        'total_tenants': len(tenants_data),
        'tenants': tenants_data
    })