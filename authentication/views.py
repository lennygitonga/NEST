from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
import pyotp
from django.utils.crypto import get_random_string
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)


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
        tokens = get_tokens_for_user(user)
        return Response({
            'message': 'Registration successful.',
            'user': UserSerializer(user).data,
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request, username=email, password=password)
        if user:
            if user.profile.is_2fa_enabled:
                return Response({
                    'message': '2FA required.',
                    'status': '2fa_required',
                    'uid': urlsafe_base64_encode(force_bytes(user.pk))
                }, status=status.HTTP_200_OK)
            tokens = get_tokens_for_user(user)
            return Response({
                'message': 'Login successful.',
                'user': UserSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_200_OK)
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