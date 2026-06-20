from rest_framework import serializers
from .models import AdminActionLog, Warning, FraudReport


class AdminActionLogSerializer(serializers.ModelSerializer):
    admin_email = serializers.EmailField(source='admin.email', read_only=True)
    target_user_email = serializers.EmailField(source='target_user.email', read_only=True)
    target_agency_name = serializers.CharField(source='target_agency.name', read_only=True)

    class Meta:
        model = AdminActionLog
        fields = [
            'id', 'action_type', 'admin', 'admin_email',
            'target_user', 'target_user_email',
            'target_agency', 'target_agency_name',
            'reason', 'created_at'
        ]


class BanUserSerializer(serializers.Serializer):
    reason = serializers.CharField()


class SuspendAgencySerializer(serializers.Serializer):
    reason = serializers.CharField()


class WarningSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    issued_by_email = serializers.EmailField(source='issued_by.email', read_only=True)

    class Meta:
        model = Warning
        fields = ['id', 'user', 'user_email', 'issued_by', 'issued_by_email', 'reason', 'created_at']
        read_only_fields = ['issued_by', 'created_at']


class PenalizeAgencySerializer(serializers.Serializer):
    new_commission_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    reason = serializers.CharField()


class FraudReportSerializer(serializers.ModelSerializer):
    reporter_email = serializers.EmailField(source='reporter.email', read_only=True)
    agency_name = serializers.CharField(source='reported_agency.name', read_only=True)

    class Meta:
        model = FraudReport
        fields = [
            'id', 'reporter', 'reporter_email', 'reported_agency', 'agency_name',
            'reason', 'status', 'admin_notes', 'created_at', 'reviewed_at'
        ]
        read_only_fields = ['reporter', 'status', 'admin_notes', 'created_at', 'reviewed_at']


class FraudReportReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudReport
        fields = ['status', 'admin_notes']