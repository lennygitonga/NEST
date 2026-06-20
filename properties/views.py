from rest_framework import status
from core.ai_utils import ask_groq
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Property, PropertyImage, PropertyDocument, PropertyApplication, Lease
from .serializers import (
    PropertySerializer, PropertyApplicationSerializer,
    ApplicationReviewSerializer, LeaseSerializer,
    PropertyImageSerializer, PropertyDocumentSerializer
)


def is_agency(user):
    return user.profile.role == 'AGENCY'


def is_tenant(user):
    return user.profile.role == 'TENANT'


def is_landlord(user):
    return user.profile.role == 'LANDLORD'


@api_view(['GET'])
@permission_classes([AllowAny])
def property_list_view(request):
    properties = Property.objects.filter(is_vacant=True, is_published=True)
    property_type = request.query_params.get('type')
    city = request.query_params.get('city')
    min_rent = request.query_params.get('min_rent')
    max_rent = request.query_params.get('max_rent')
    if property_type:
        properties = properties.filter(property_type=property_type)
    if city:
        properties = properties.filter(city__icontains=city)
    if min_rent:
        properties = properties.filter(rent_amount__gte=min_rent)
    if max_rent:
        properties = properties.filter(rent_amount__lte=max_rent)
    serializer = PropertySerializer(properties, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def property_create_view(request):
    if not is_agency(request.user):
        return Response({'error': 'Only agencies can create properties.'}, status=status.HTTP_403_FORBIDDEN)
    if not request.user.agency.is_verified:
        return Response({'error': 'Your agency must be verified before listing properties.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = PropertySerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Property created successfully.',
            'property': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def property_detail_view(request, pk):
    property = get_object_or_404(Property, pk=pk)
    serializer = PropertySerializer(property)
    return Response(serializer.data)


@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
def property_update_view(request, pk):
    if not is_agency(request.user):
        return Response({'error': 'Only agencies can update properties.'}, status=status.HTTP_403_FORBIDDEN)
    property = get_object_or_404(Property, pk=pk, agency=request.user.agency)
    serializer = PropertySerializer(property, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Property updated successfully.',
            'property': serializer.data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def property_delete_view(request, pk):
    if not is_agency(request.user):
        return Response({'error': 'Only agencies can delete properties.'}, status=status.HTTP_403_FORBIDDEN)
    property = get_object_or_404(Property, pk=pk, agency=request.user.agency)
    property.delete()
    return Response({'message': 'Property deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def property_image_upload_view(request, pk):
    if not is_agency(request.user):
        return Response({'error': 'Only agencies can upload property images.'}, status=status.HTTP_403_FORBIDDEN)
    property = get_object_or_404(Property, pk=pk, agency=request.user.agency)
    serializer = PropertyImageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(property=property)
        return Response({'message': 'Image uploaded successfully.', 'image': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def property_document_upload_view(request, pk):
    if not is_agency(request.user):
        return Response({'error': 'Only agencies can upload property documents.'}, status=status.HTTP_403_FORBIDDEN)
    property = get_object_or_404(Property, pk=pk, agency=request.user.agency)
    serializer = PropertyDocumentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(property=property)
        return Response({'message': 'Document uploaded successfully.', 'document': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def application_list_create_view(request):
    if request.method == 'GET':
        if is_agency(request.user):
            applications = PropertyApplication.objects.filter(property__agency=request.user.agency)
        elif is_tenant(request.user):
            applications = PropertyApplication.objects.filter(tenant=request.user)
        else:
            return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = PropertyApplicationSerializer(applications, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        if not is_tenant(request.user):
            return Response({'error': 'Only tenants can apply for properties.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = PropertyApplicationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Application submitted successfully.',
                'application': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def application_review_view(request, pk):
    if not is_agency(request.user):
        return Response({'error': 'Only agencies can review applications.'}, status=status.HTTP_403_FORBIDDEN)
    application = get_object_or_404(PropertyApplication, pk=pk)
    serializer = ApplicationReviewSerializer(application, data=request.data, partial=True)
    if serializer.is_valid():
        from django.utils import timezone
        application.status = request.data.get('status', application.status)
        application.reviewed_at = timezone.now()
        application.save()
        return Response({'message': f'Application {application.status.lower()} successfully.'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def lease_list_create_view(request):
    if request.method == 'GET':
        if is_agency(request.user):
            leases = Lease.objects.filter(agency=request.user.agency)
        elif is_tenant(request.user):
            leases = Lease.objects.filter(tenant=request.user)
        elif is_landlord(request.user):
            leases = Lease.objects.filter(property__landlord=request.user)
        else:
            return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = LeaseSerializer(leases, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        if not is_agency(request.user):
            return Response({'error': 'Only agencies can create leases.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = LeaseSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            lease = serializer.save()
            lease.property.is_vacant = False
            lease.property.save()
            return Response({
                'message': 'Lease created successfully.',
                'lease': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lease_detail_view(request, pk):
    if is_agency(request.user):
        lease = get_object_or_404(Lease, pk=pk, agency=request.user.agency)
    elif is_tenant(request.user):
        lease = get_object_or_404(Lease, pk=pk, tenant=request.user)
    elif is_landlord(request.user):
        lease = get_object_or_404(Lease, pk=pk, property__landlord=request.user)
    else:
        return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = LeaseSerializer(lease)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lease_summary_view(request, pk):
    if is_agency(request.user):
        lease = get_object_or_404(Lease, pk=pk, agency=request.user.agency)
    elif is_tenant(request.user):
        lease = get_object_or_404(Lease, pk=pk, tenant=request.user)
    elif is_landlord(request.user):
        lease = get_object_or_404(Lease, pk=pk, property__landlord=request.user)
    else:
        return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)

    prompt = (
        f"Summarize this lease agreement in simple, friendly, plain English for a tenant who is not familiar with legal terms:\n\n"
        f"Property: {lease.property.title}\n"
        f"Address: {lease.property.address}, {lease.property.city}\n"
        f"Tenant: {lease.tenant.first_name} {lease.tenant.last_name}\n"
        f"Rent Amount: KSh {lease.rent_amount}\n"
        f"Lease Start Date: {lease.start_date}\n"
        f"Lease End Date: {lease.end_date}\n"
        f"Status: {'Active' if lease.is_active else 'Inactive'}\n\n"
        f"Write a short, warm 3-4 sentence summary explaining what this means for the tenant, when rent is due, and when the lease ends. "
        f"Do not use legal jargon."
    )

    summary = ask_groq(prompt, system_prompt="You are a friendly property assistant who explains lease terms simply.")

    return Response({
        'lease_id': lease.id,
        'summary': summary
    })