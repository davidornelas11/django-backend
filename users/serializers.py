from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, RefreshToken

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birth_date', 'created_at', 'updated_at', 'latitude', 'longitude', 'status', 'scraped_data']
        read_only_fields = ['created_at', 'updated_at', 'status', 'scraped_data']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id']

class TokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user = UserSerializer() 
        