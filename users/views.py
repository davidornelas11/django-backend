from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework import generics
from .serializers import UserSerializer, ProfileSerializer, TokenSerializer
from .models import Profile, RefreshToken
from datetime import datetime

# Create your views here.

class RegisterRateThrottle(AnonRateThrottle):
    rate = '5/hour'

class LoginRateThrottle(AnonRateThrottle):
    rate = '5/minute'  # Stricter rate limit for login attempts

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([RegisterRateThrottle])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if not username or not password or not email:
        return Response(
            {'error': 'Please provide username, password and email'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate password strength
    try:
        validate_password(password)
    except ValidationError as e:
        return Response(
            {'error': list(e.messages)},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Email already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    # Create access token
    access_token, _ = Token.objects.get_or_create(user=user)
    
    # Create refresh token
    refresh_token = RefreshToken.create_token(user)

    return Response({
        'access_token': access_token.key,
        'refresh_token': refresh_token.token,
        'user': UserSerializer(user).data
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])  # Use the new throttle class
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Please provide username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if not user:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    login(request, user)
    
    # Create access token
    access_token, _ = Token.objects.get_or_create(user=user)
    
    # Create refresh token
    refresh_token = RefreshToken.create_token(user)

    return Response({
        'access_token': access_token.key,
        'refresh_token': refresh_token.token,
        'user': UserSerializer(user).data
    })

@api_view(['POST'])
@throttle_classes([UserRateThrottle])
def logout_view(request):
    if request.user.is_authenticated:
        # Invalidate refresh token
        RefreshToken.objects.filter(user=request.user).update(is_valid=False)
        # Delete access token
        request.user.auth_token.delete()
        logout(request)
    return Response({'message': 'Successfully logged out'})

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    refresh_token = request.data.get('refresh_token')
    
    if not refresh_token:
        return Response(
            {'error': 'Refresh token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        token_obj = RefreshToken.objects.get(
            token=refresh_token,
            is_valid=True,
            expires_at__gt=datetime.now()
        )
        
        # Create new access token
        access_token, _ = Token.objects.get_or_create(user=token_obj.user)
        
        return Response({
            'access_token': access_token.key,
            'user': UserSerializer(token_obj.user).data
        })
    except RefreshToken.DoesNotExist:
        return Response(
            {'error': 'Invalid or expired refresh token'},
            status=status.HTTP_401_UNAUTHORIZED
        )

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    
    def get_object(self):
        return self.request.user.profile

@api_view(['PUT'])
def update_location(request):
    location = request.data.get('location')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    if not location:
        return Response(
            {'error': 'Location is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    profile = request.user.profile
    profile.location = location
    if latitude is not None:
        try:
            profile.latitude = float(latitude)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid latitude value'}, status=status.HTTP_400_BAD_REQUEST)
    if longitude is not None:
        try:
            profile.longitude = float(longitude)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid longitude value'}, status=status.HTTP_400_BAD_REQUEST)
    profile.save()
    
    return Response({
        'message': 'Location updated successfully',
        'location': location,
        'latitude': profile.latitude,
        'longitude': profile.longitude
    }, status=status.HTTP_200_OK)
