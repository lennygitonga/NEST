from rest_framework import serializers
from .models import Agency, AgencyLandlord
from authentication.serializers import UserSerializer


class AgencySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Agency
        fields = [
            'id', 'user', 'name', 'registration_number', 'logo',
            'address', 'phone_number', 'email', 'website',
            'is_verified', 'commission_rate', 'created_at'
        ]
        read_only_fields = ['is_verified', 'commission_rate', 'created_at']


class AgencyRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = [
            'name', 'registration_number', 'logo',
            'address', 'phone_number', 'email', 'website'
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        agency = Agency.objects.create(user=user, **validated_data)
        return agency


class AgencyVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ['is_verified']


class AgencyLandlordSerializer(serializers.ModelSerializer):
    landlord_email = serializers.EmailField(source='landlord.email', read_only=True)
    landlord_name = serializers.SerializerMethodField()

    class Meta:
        model = AgencyLandlord
        fields = [
            'id', 'agency', 'landlord', 'landlord_email', 'landlord_name',
            'status', 'management_fee_percent', 'joined_at'
        ]
        read_only_fields = ['joined_at']

    def get_landlord_name(self, obj):
        return f"{obj.landlord.first_name} {obj.landlord.last_name}".strip() or obj.landlord.email


class AgencyDashboardSerializer(serializers.ModelSerializer):
    total_properties = serializers.SerializerMethodField()
    vacant_properties = serializers.SerializerMethodField()
    occupied_properties = serializers.SerializerMethodField()
    total_landlords = serializers.SerializerMethodField()

    class Meta:
        model = Agency
        fields = [
            'id', 'name', 'is_verified', 'commission_rate',
            'total_properties', 'vacant_properties',
            'occupied_properties', 'total_landlords'
        ]

    def get_total_properties(self, obj):
        return obj.properties.count()

    def get_vacant_properties(self, obj):
        return obj.properties.filter(is_vacant=True).count()

    def get_occupied_properties(self, obj):
        return obj.properties.filter(is_vacant=False).count()

    def get_total_landlords(self, obj):
        return obj.landlords.filter(status='ACTIVE').count()