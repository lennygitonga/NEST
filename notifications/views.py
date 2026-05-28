from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Notification
from .serializers import NotificationSerializer, NotificationMarkReadSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list_view(request):
    notifications = Notification.objects.filter(recipient=request.user)

    # Filter by read/unread if provided
    is_read = request.query_params.get('is_read')
    if is_read is not None:
        notifications = notifications.filter(is_read=is_read.lower() == 'true')

    serializer = NotificationSerializer(notifications, many=True)
    return Response({
        'total': notifications.count(),
        'unread': notifications.filter(is_read=False).count(),
        'notifications': serializer.data
    })


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def notification_mark_read_view(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    serializer = NotificationMarkReadSerializer(notification, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Notification marked as read.'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def notification_mark_all_read_view(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return Response({'message': 'All notifications marked as read.'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def notification_delete_view(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.delete()
    return Response({'message': 'Notification deleted.'}, status=status.HTTP_204_NO_CONTENT)