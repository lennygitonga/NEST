from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import MaintenanceTicket, TicketComment
from .serializers import (
    MaintenanceTicketSerializer,
    TicketStatusUpdateSerializer,
    TicketCommentSerializer
)


def is_agency(user):
    return user.profile.role == 'AGENCY'


def is_tenant(user):
    return user.profile.role == 'TENANT'


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def ticket_list_create_view(request):
    if request.method == 'GET':
        if is_agency(request.user):
            tickets = MaintenanceTicket.objects.filter(
                property__agency=request.user.agency
            )
            # Filter by status if provided
            ticket_status = request.query_params.get('status')
            priority = request.query_params.get('priority')
            if ticket_status:
                tickets = tickets.filter(status=ticket_status)
            if priority:
                tickets = tickets.filter(priority=priority)
        elif is_tenant(request.user):
            tickets = MaintenanceTicket.objects.filter(reported_by=request.user)
        else:
            return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = MaintenanceTicketSerializer(tickets, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        if not is_tenant(request.user):
            return Response({'error': 'Only tenants can file maintenance tickets.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = MaintenanceTicketSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Maintenance ticket filed successfully.',
                'ticket': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ticket_detail_view(request, pk):
    if is_agency(request.user):
        ticket = get_object_or_404(MaintenanceTicket, pk=pk, property__agency=request.user.agency)
    elif is_tenant(request.user):
        ticket = get_object_or_404(MaintenanceTicket, pk=pk, reported_by=request.user)
    else:
        return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = MaintenanceTicketSerializer(ticket)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def ticket_status_update_view(request, pk):
    if not is_agency(request.user):
        return Response({'error': 'Only agencies can update ticket status.'}, status=status.HTTP_403_FORBIDDEN)
    ticket = get_object_or_404(MaintenanceTicket, pk=pk, property__agency=request.user.agency)
    serializer = TicketStatusUpdateSerializer(ticket, data=request.data, partial=True)
    if serializer.is_valid():
        if request.data.get('status') == 'RESOLVED':
            ticket.resolved_at = timezone.now()
        serializer.save()
        return Response({
            'message': 'Ticket updated successfully.',
            'ticket': serializer.data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def ticket_comment_list_create_view(request, pk):
    if is_agency(request.user):
        ticket = get_object_or_404(MaintenanceTicket, pk=pk, property__agency=request.user.agency)
    elif is_tenant(request.user):
        ticket = get_object_or_404(MaintenanceTicket, pk=pk, reported_by=request.user)
    else:
        return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        comments = TicketComment.objects.filter(ticket=ticket)
        serializer = TicketCommentSerializer(comments, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = TicketCommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(ticket=ticket)
            return Response({
                'message': 'Comment added successfully.',
                'comment': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)