from rest_framework import serializers
from .models import Property, PropertyImage, PropertyDocument, PropertyApplication, Lease


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'uploaded_at']


class PropertyDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyDocument
        fields = ['id', 'document', 'label', 'uploaded_at']


class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    documents = PropertyDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'agency', 'landlord', 'title', 'description',
            'property_type', 'address', 'city', 'rent_amount',
            'bedrooms', 'bathrooms', 'is_vacant', 'is_published',
            'images', 'documents', 'created_at', 'updated_at'
        ]
        read_only_fields = ['agency', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context['request']
        agency = request.user.agency
        validated_data['agency'] = agency
        return super().create(validated_data)


class PropertyApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyApplication
        fields = [
            'id', 'tenant', 'property', 'status',
            'message', 'applied_at', 'reviewed_at'
        ]
        read_only_fields = ['tenant', 'status', 'applied_at', 'reviewed_at']

    def create(self, validated_data):
        request = self.context['request']
        validated_data['tenant'] = request.user
        return super().create(validated_data)


class ApplicationReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyApplication
        fields = ['status', 'reviewed_at']


class LeaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lease
        fields = [
            'id', 'tenant', 'property', 'agency',
            'start_date', 'end_date', 'rent_amount',
            'lease_document', 'is_active', 'created_at'
        ]
        read_only_fields = ['agency', 'created_at']

    def create(self, validated_data):
        request = self.context['request']
        validated_data['agency'] = request.user.agency
        return super().create(validated_data)