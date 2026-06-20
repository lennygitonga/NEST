from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from agencies.models import Agency
from .models import AdminActionLog, Warning, FraudReport
from .serializers import (
    AdminActionLogSerializer, BanUserSerializer, SuspendAgencySerializer,
    WarningSerializer, PenalizeAgencySerializer,
    FraudReportSerializer, FraudReportReviewSerializer
)


def is_nest_admin(user):
    return user.profile.role == 'NEST_ADMIN'


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ban_user_view(request, user_id):
    if not is_nest_admin(request.user):
        return Response({'error': 'Only NEST admins can ban users.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = BanUserSerializer(data=request.data)
    if serializer.is_valid():
        target_user = get_object_or_404(User, pk=user_id)
        target_user.profile.is_banned = True
        target_user.profile.ban_reason = serializer.validated_data['reason']
        target_user.profile.save()

        AdminActionLog.objects.create(
            admin=request.user,
            action_type='BAN_USER',
            target_user=target_user,
            reason=serializer.validated_data['reason']
        )

        return Response({'message': f'{target_user.email} has been banned.'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unban_user_view(request, user_id):
    if not is_nest_admin(request.user):
        return Response({'error': 'Only NEST admins can unban users.'}, status=status.HTTP_403_FORBIDDEN)

    target_user = get_object_or_404(User, pk=user_id)
    target_user.profile.is_banned = False
    target_user.profile.ban_reason = None
    target_user.profile.save()

    AdminActionLog.objects.create(
        admin=request.user,
        action_type='UNBAN_USER',
        target_user=target_user,
        reason='Account unbanned by admin.'
    )

    return Response({'message': f'{target_user.email} has been unbanned.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def suspend_agency_view(request, agency_id):
    if not is_nest_admin(request.user):
        return Response({'error': 'Only NEST admins can suspend agencies.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = SuspendAgencySerializer(data=request.data)
    if serializer.is_valid():
        agency = get_object_or_404(Agency, pk=agency_id)
        agency.is_suspended = True
        agency.suspension_reason = serializer.validated_data['reason']
        agency.save()

        # Unpublish all their properties
        agency.properties.update(is_published=False)

        AdminActionLog.objects.create(
            admin=request.user,
            action_type='SUSPEND_AGENCY',
            target_agency=agency,
            reason=serializer.validated_data['reason']
        )

        return Response({'message': f'{agency.name} has been suspended.'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unsuspend_agency_view(request, agency_id):
    if not is_nest_admin(request.user):
        return Response({'error': 'Only NEST admins can unsuspend agencies.'}, status=status.HTTP_403_FORBIDDEN)

    agency = get_object_or_404(Agency, pk=agency_id)
    agency.is_suspended = False
    agency.suspension_reason = None
    agency.save()

    agency.properties.update(is_published=True)

    AdminActionLog.objects.create(
        admin=request.user,
        action_type='UNSUSPEND_AGENCY',
        target_agency=agency,
        reason='Agency unsuspended by admin.'
    )

    return Response({'message': f'{agency.name} has been unsuspended.'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_delete_user_view(request, user_id):
    if not is_nest_admin(request.user):
        return Response({'error': 'Only NEST admins can delete users.'}, status=status.HTTP_403_FORBIDDEN)

    target_user = get_object_or_404(User, pk=user_id)
    reason = request.data.get('reason', 'No reason provided.')
    email = target_user.email

    AdminActionLog.objects.create(
        admin=request.user,
        action_type='DELETE_USER',
        reason=f"Deleted {email}. Reason: {reason}"
    )

    target_user.delete()

    return Response({'message': f'{email} has been permanently deleted.'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def issue_warning_view(request, user_id):
    if not is_nest_admin(request.user):
        return Response({'error': 'Only NEST admins can issue warnings.'}, status=status.HTTP_403_FORBIDDEN)

    target_user = get_object_or_404(User, pk=user_id)
    reason = request.data.get('reason')

    if not reason:
        return Response({'error': 'Reason is required.'}, status=status.HTTP_400_BAD_REQUEST)

    warning = Warning.objects.create(
        user=target_user,
        issued_by=request.user,
        reason=reason
    )

    AdminActionLog.objects.create(
        admin=request.user,
        action_type='WARN_USER',
        target_user=target_user,
        reason=reason
    )

    return Response({
        'message': f'Warning issued to {target_user.email}.',
        'warning': WarningSerializer(warning).data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_warnings_view(request):
    warnings = Warning.objects.filter(user=request.user)
    serializer = WarningSerializer(warnings, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def penalize_agency_view(request, agency_id):
    if not is_nest_admin(request.user):
        return Response({'error': 'Only NEST admins can penalize agencies.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = PenalizeAgencySerializer(data=request.data)
    if serializer.is_valid():
        agency = get_object_or_404(Agency, pk=agency_id)
        old_rate = agency.commission_rate
        agency.commission_rate = serializer.validated_data['new_commission_rate']
        agency.save()

        AdminActionLog.objects.create(
            admin=request.user,
            action_type='PENALIZE_AGENCY',
            target_agency=agency,
            reason=f"{serializer.validated_data['reason']} (Commission changed from {old_rate}% to {agency.commission_rate}%)"
        )

        return Response({
            'message': f'{agency.name} commission rate updated to {agency.commission_rate}%.'
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def file_fraud_report_view(request):
    serializer = FraudReportSerializer(data=request.data)
    if serializer.is_valid():
        agency_id = request.data.get('reported_agency')
        agency = get_object_or_404(Agency, pk=agency_id)
        report = FraudReport.objects.create(
            reporter=request.user,
            reported_agency=agency,
            reason=serializer.validated_data['reason']
        )
        return Response({
            'message': 'Fraud report filed successfully. Our team will review it.',
            'report': FraudReportSerializer(report).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_fraud_reports_view(request):
    if not is_nest_admin(request.user):
        return Response({'error': 'Only NEST admins can view fraud reports.'}, status=status.HTTP_403_FORBIDDEN)
    reports = FraudReport.objects.all()
    serializer = FraudReportSerializer(reports, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def review_fraud_report_view(request, report_id):
    if not is_nest_admin(request.user):
        return Response({'error': 'Only NEST admins can review fraud reports.'}, status=status.HTTP_403_FORBIDDEN)

    report = get_object_or_404(FraudReport, pk=report_id)
    serializer = FraudReportReviewSerializer(report, data=request.data, partial=True)
    if serializer.is_valid():
        report.reviewed_at = timezone.now()
        serializer.save()
        return Response({'message': 'Fraud report updated successfully.'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_log_view(request):
    if not is_nest_admin(request.user):
        return Response({'error': 'Only NEST admins can view the audit log.'}, status=status.HTTP_403_FORBIDDEN)
    logs = AdminActionLog.objects.all()
    serializer = AdminActionLogSerializer(logs, many=True)
    return Response(serializer.data)