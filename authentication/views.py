import random
from django.utils import timezone
from datetime import timedelta
from .serializers import AccountDeletionRequestSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from drf_spectacular.utils import extend_schema
import pyotp
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    ProfileUpdateSerializer, ChangePasswordSerializer, ChangeEmailSerializer
)
from django.utils.crypto import get_random_string
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        send_verification_email(user)
        tokens = get_tokens_for_user(user)
        return Response({
            'message': 'Registration successful. Please check your email for a verification code.',
            'user': UserSerializer(user).data,
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=LoginSerializer, responses={200: UserSerializer})
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request, username=email, password=password)
        if user:
            if not user.profile.is_email_verified:
                return Response({
                    'error': 'Please verify your email before logging in.',
                    'status': 'email_not_verified'
                }, status=status.HTTP_403_FORBIDDEN)
            if user.profile.is_2fa_enabled:
                return Response({
                    'message': '2FA required.',
                    'status': '2fa_required',
                    'uid': urlsafe_base64_encode(force_bytes(user.pk))
                }, status=status.HTTP_200_OK)
            tokens = get_tokens_for_user(user)
            response_data = {
                'message': 'Login successful.',
                'user': UserSerializer(user).data,
                'tokens': tokens
            }
            if user.profile.is_pending_deletion:
                deletion_date = user.profile.deletion_requested_at + timedelta(days=7)
                response_data['warning'] = 'Your account is scheduled for deletion.'
                response_data['deletion_date'] = deletion_date
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request_view(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"http://localhost:3000/reset-password?uid={uid}&token={token}"
            send_mail(
                subject='NEST — Password Reset Request',
                message=f'Click the link below to reset your password:\n\n{reset_link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except User.DoesNotExist:
            pass
        return Response({'message': 'If that email exists, a reset link has been sent.'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm_view(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
            user = User.objects.get(pk=uid)
            token = serializer.validated_data['token']
            if default_token_generator.check_token(user, token):
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({'message': 'Password reset successful.'})
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'Invalid user.'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_2fa_view(request):
    profile = request.user.profile
    if profile.is_2fa_enabled:
        return Response({'error': '2FA is already enabled.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate a secret key for this user
    secret = pyotp.random_base32()
    profile.totp_secret = secret
    profile.save()

    # Generate QR code URI for Google Authenticator
    totp = pyotp.TOTP(secret)
    qr_uri = totp.provisioning_uri(
        name=request.user.email,
        issuer_name='NEST Property Management'
    )

    return Response({
        'message': 'Scan the QR code URI with Google Authenticator.',
        'secret': secret,
        'qr_uri': qr_uri
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_2fa_setup_view(request):
    code = request.data.get('code')
    if not code:
        return Response({'error': 'Code is required.'}, status=status.HTTP_400_BAD_REQUEST)

    profile = request.user.profile
    if not profile.totp_secret:
        return Response({'error': 'Please set up 2FA first.'}, status=status.HTTP_400_BAD_REQUEST)

    totp = pyotp.TOTP(profile.totp_secret)
    if totp.verify(code):
        profile.is_2fa_enabled = True
        profile.save()
        return Response({'message': '2FA enabled successfully.'})
    return Response({'error': 'Invalid code. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_2fa_login_view(request):
    uid = request.data.get('uid')
    code = request.data.get('code')

    if not uid or not code:
        return Response({'error': 'UID and code are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, ValueError):
        return Response({'error': 'Invalid user.'}, status=status.HTTP_400_BAD_REQUEST)

    totp = pyotp.TOTP(user.profile.totp_secret)
    if totp.verify(code):
        tokens = get_tokens_for_user(user)
        return Response({
            'message': 'Login successful.',
            'user': UserSerializer(user).data,
            'tokens': tokens
        })
    return Response({'error': 'Invalid or expired code.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_2fa_view(request):
    code = request.data.get('code')
    if not code:
        return Response({'error': 'Code is required to disable 2FA.'}, status=status.HTTP_400_BAD_REQUEST)

    profile = request.user.profile
    if not profile.is_2fa_enabled:
        return Response({'error': '2FA is not enabled.'}, status=status.HTTP_400_BAD_REQUEST)

    totp = pyotp.TOTP(profile.totp_secret)
    if totp.verify(code):
        profile.is_2fa_enabled = False
        profile.totp_secret = None
        profile.save()
        return Response({'message': '2FA disabled successfully.'})
    return Response({'error': 'Invalid code.'}, status=status.HTTP_400_BAD_REQUEST)

def generate_verification_code():
    return str(random.randint(100000, 999999))


def send_verification_email(user):
    code = generate_verification_code()
    profile = user.profile
    profile.email_verification_code = code
    profile.email_verification_sent_at = timezone.now()
    profile.save()

    send_mail(
        subject='NEST — Verify Your Email',
        message=f'Your verification code is: {code}\n\nThis code expires in 15 minutes.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_view(request):
    email = request.data.get('email')
    code = request.data.get('code')

    if not email or not code:
        return Response({'error': 'Email and code are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    profile = user.profile

    if profile.is_email_verified:
        return Response({'message': 'Email is already verified.'})

    if not profile.email_verification_code:
        return Response({'error': 'No verification code found. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if code expired (15 minutes)
    if timezone.now() > profile.email_verification_sent_at + timezone.timedelta(minutes=15):
        return Response({'error': 'Verification code has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

    if profile.email_verification_code != code:
        return Response({'error': 'Invalid verification code.'}, status=status.HTTP_400_BAD_REQUEST)

    profile.is_email_verified = True
    profile.email_verification_code = None
    profile.save()

    return Response({'message': 'Email verified successfully.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_view(request):
    email = request.data.get('email')

    if not email:
        return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    if user.profile.is_email_verified:
        return Response({'message': 'Email is already verified.'})

    send_verification_email(user)
    return Response({'message': 'Verification code sent successfully.'})

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def profile_update_view(request):
    profile = request.user.profile
    serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profile updated successfully.',
            'user': UserSerializer(request.user).data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(old_password):
            return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password changed successfully.'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_email_view(request):
    serializer = ChangeEmailSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        new_email = serializer.validated_data['new_email']
        password = serializer.validated_data['password']

        if not user.check_password(password):
            return Response({'error': 'Password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
            return Response({'error': 'This email is already in use.'}, status=status.HTTP_400_BAD_REQUEST)

        user.email = new_email
        user.username = new_email
        user.save()

        user.profile.is_email_verified = False
        user.profile.save()

        send_verification_email(user)

        return Response({'message': 'Email updated. Please verify your new email address.'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_account_deletion_view(request):
    serializer = AccountDeletionRequestSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        password = serializer.validated_data['password']

        if not user.check_password(password):
            return Response({'error': 'Incorrect password.'}, status=status.HTTP_400_BAD_REQUEST)

        profile = user.profile
        if profile.is_pending_deletion:
            return Response({'error': 'Account deletion is already pending.'}, status=status.HTTP_400_BAD_REQUEST)

        # Agency specific check — block deletion if active leases exist
        if profile.is_agency() and hasattr(user, 'agency'):
            from properties.models import Lease
            active_leases = Lease.objects.filter(agency=user.agency, is_active=True).count()
            if active_leases > 0:
                return Response({
                    'error': f'Cannot delete account. You have {active_leases} active lease(s). Please transfer or end them first.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Unpublish all properties during grace period
            user.agency.properties.update(is_published=False)

        profile.is_pending_deletion = True
        profile.deletion_requested_at = timezone.now()
        profile.save()

        send_mail(
            subject='NEST — Account Deletion Requested',
            message=(
                'You have requested to delete your NEST account.\n\n'
                'Your account will be permanently deleted in 7 days.\n\n'
                'If you change your mind, simply log in before then and cancel the deletion.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({
            'message': 'Account deletion requested. Your account will be permanently deleted in 7 days unless you cancel.',
            'deletion_date': profile.deletion_requested_at + timedelta(days=7)
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_account_deletion_view(request):
    profile = request.user.profile

    if not profile.is_pending_deletion:
        return Response({'error': 'No pending deletion to cancel.'}, status=status.HTTP_400_BAD_REQUEST)

    profile.is_pending_deletion = False
    profile.deletion_requested_at = None
    profile.save()

    # Restore agency properties if applicable
    user = request.user
    if profile.is_agency() and hasattr(user, 'agency'):
        user.agency.properties.update(is_published=True)

    return Response({'message': 'Account deletion cancelled. Welcome back!'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def deletion_status_view(request):
    profile = request.user.profile

    if not profile.is_pending_deletion:
        return Response({'is_pending_deletion': False})

    deletion_date = profile.deletion_requested_at + timedelta(days=7)
    days_remaining = (deletion_date - timezone.now()).days

    return Response({
        'is_pending_deletion': True,
        'deletion_requested_at': profile.deletion_requested_at,
        'deletion_date': deletion_date,
        'days_remaining': max(days_remaining, 0)
    })