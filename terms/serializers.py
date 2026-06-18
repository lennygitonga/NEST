from rest_framework import serializers
from .models import TermsAndConditions, UserTermsAcceptance


class TermsAndConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsAndConditions
        fields = ['id', 'version', 'title', 'content', 'is_active', 'created_at']


class TermsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsAndConditions
        fields = ['version', 'title', 'content', 'is_active']


class UserTermsAcceptanceSerializer(serializers.ModelSerializer):
    terms_version = serializers.CharField(source='terms.version', read_only=True)

    class Meta:
        model = UserTermsAcceptance
        fields = ['id', 'terms', 'terms_version', 'accepted_at']
        read_only_fields = ['accepted_at']