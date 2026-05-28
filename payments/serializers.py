from rest_framework import serializers
from .models import RentPayment, Payout, TenantCreditScore


class RentPaymentSerializer(serializers.ModelSerializer):
    tenant_email = serializers.EmailField(source='tenant.email', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)

    class Meta:
        model = RentPayment
        fields = [
            'id', 'tenant', 'tenant_email', 'property', 'property_title',
            'lease', 'agency', 'total_amount', 'nest_commission',
            'agency_earnings', 'payment_method', 'transaction_id',
            'status', 'payment_date', 'payment_for_month'
        ]
        read_only_fields = [
            'tenant', 'agency', 'nest_commission',
            'agency_earnings', 'payment_date'
        ]

    def create(self, validated_data):
        request = self.context['request']
        validated_data['tenant'] = request.user
        validated_data['agency'] = validated_data['property'].agency
        return super().create(validated_data)


class PayoutSerializer(serializers.ModelSerializer):
    recipient_email = serializers.EmailField(source='recipient.email', read_only=True)

    class Meta:
        model = Payout
        fields = [
            'id', 'recipient', 'recipient_email', 'payout_type',
            'amount', 'status', 'month', 'processed_at',
            'notes', 'created_at'
        ]
        read_only_fields = ['created_at']


class TenantCreditScoreSerializer(serializers.ModelSerializer):
    tenant_email = serializers.EmailField(source='tenant.email', read_only=True)

    class Meta:
        model = TenantCreditScore
        fields = [
            'id', 'tenant', 'tenant_email', 'score',
            'total_payments', 'on_time_payments',
            'late_payments', 'missed_payments', 'last_updated'
        ]
        read_only_fields = [
            'tenant', 'score', 'total_payments', 'on_time_payments',
            'late_payments', 'missed_payments', 'last_updated'
        ]


class MonthlyReportSerializer(serializers.Serializer):
    month = serializers.DateField()
    total_collected = serializers.DecimalField(max_digits=10, decimal_places=2)
    nest_commission = serializers.DecimalField(max_digits=10, decimal_places=2)
    agency_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_payments = serializers.IntegerField()