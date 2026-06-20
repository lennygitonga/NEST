from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role', 'phone_number', 'profile_photo', 'id_document', 'is_2fa_enabled', 'is_email_verified']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=['AGENCY', 'LANDLORD', 'TENANT'])
    accept_terms = serializers.BooleanField(write_only=True)

    # Agency specific fields — only required if role is AGENCY
    agency_name = serializers.CharField(write_only=True, required=False)
    registration_number = serializers.CharField(write_only=True, required=False)
    agency_address = serializers.CharField(write_only=True, required=False)
    agency_phone = serializers.CharField(write_only=True, required=False)
    agency_website = serializers.URLField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'password', 'role', 'accept_terms',
            'agency_name', 'registration_number', 'agency_address', 'agency_phone', 'agency_website'
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_accept_terms(self, value):
        if not value:
            raise serializers.ValidationError("You must accept the Terms and Conditions to register.")
        return value

    def validate(self, data):
        if data.get('role') == 'AGENCY':
            required_fields = ['agency_name', 'registration_number', 'agency_address', 'agency_phone']
            missing = [f for f in required_fields if not data.get(f)]
            if missing:
                raise serializers.ValidationError({
                    field: 'This field is required for agency registration.' for field in missing
                })
        return data

    def create(self, validated_data):
        role = validated_data.pop('role')
        validated_data.pop('accept_terms')

        # Pop agency fields
        agency_name = validated_data.pop('agency_name', None)
        registration_number = validated_data.pop('registration_number', None)
        agency_address = validated_data.pop('agency_address', None)
        agency_phone = validated_data.pop('agency_phone', None)
        agency_website = validated_data.pop('agency_website', None)

        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        user.profile.role = role
        user.profile.save()

        if role == 'AGENCY':
            from agencies.models import Agency
            Agency.objects.create(
                user=user,
                name=agency_name,
                registration_number=registration_number,
                address=agency_address,
                phone_number=agency_phone,
                email=user.email,
                website=agency_website or ''
            )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'profile']


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    uid = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)

class ProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'phone_number', 'profile_photo', 'id_document']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if 'first_name' in user_data:
            instance.user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            instance.user.last_name = user_data['last_name']
        instance.user.save()
        return super().update(instance, validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)


class ChangeEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
    password = serializers.CharField(write_only=True) 

class AccountDeletionRequestSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)       