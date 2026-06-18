from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import TermsAndConditions, UserTermsAcceptance
from .serializers import (
    TermsAndConditionsSerializer, TermsCreateSerializer,
    UserTermsAcceptanceSerializer
)


def is_nest_admin(user):
    return user.profile.role == 'NEST_ADMIN'


@api_view(['GET'])
@permission_classes([AllowAny])
def current_terms_view(request):
    terms = TermsAndConditions.objects.filter(is_active=True).first()
    if not terms:
        return Response({'error': 'No active terms found.'}, status=status.HTTP_404_NOT_FOUND)
    serializer = TermsAndConditionsSerializer(terms)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_terms_view(request):
    if not is_nest_admin(request.user):
        return Response({'error': 'Only NEST admins can view all terms versions.'}, status=status.HTTP_403_FORBIDDEN)
    terms = TermsAndConditions.objects.all()
    serializer = TermsAndConditionsSerializer(terms, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_terms_view(request):
    if not is_nest_admin(request.user):
        return Response({'error': 'Only NEST admins can create new terms versions.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = TermsCreateSerializer(data=request.data)
    if serializer.is_valid():
        terms = serializer.save()
        return Response({
            'message': 'New terms version created successfully.',
            'terms': TermsAndConditionsSerializer(terms).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_terms_view(request):
    terms = TermsAndConditions.objects.filter(is_active=True).first()
    if not terms:
        return Response({'error': 'No active terms found.'}, status=status.HTTP_404_NOT_FOUND)

    acceptance, created = UserTermsAcceptance.objects.get_or_create(
        user=request.user,
        terms=terms
    )

    if not created:
        return Response({'message': 'You have already accepted this version of the terms.'})

    return Response({
        'message': 'Terms accepted successfully.',
        'acceptance': UserTermsAcceptanceSerializer(acceptance).data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def terms_acceptance_status_view(request):
    current_terms = TermsAndConditions.objects.filter(is_active=True).first()
    if not current_terms:
        return Response({'has_accepted_current': False, 'message': 'No active terms found.'})

    has_accepted = UserTermsAcceptance.objects.filter(
        user=request.user,
        terms=current_terms
    ).exists()

    return Response({
        'current_version': current_terms.version,
        'has_accepted_current': has_accepted
    })