from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, RefreshToken

class ProfileSerializer(serializers.ModelSerializer):
    is_email_verified = serializers.ReadOnlyField()
    
    class Meta:
        model = Profile
        fields = [
            'bio', 'location', 'birth_date', 'created_at', 'updated_at', 
            'latitude', 'longitude', 'status', 'preferences', 'dietary_restrictions',
            'weekly_budget', 'preferred_store_id', 'meal_plan', 'is_email_verified'
        ]
        read_only_fields = ['created_at', 'updated_at', 'status', 'meal_plan', 'is_email_verified']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    email_verified = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 'email_verified']
        read_only_fields = ['id', 'email_verified']
    
    def get_email_verified(self, obj):
        """Get email verification status"""
        return obj.profile.is_email_verified if hasattr(obj, 'profile') else False

class TokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user = UserSerializer()
    email_verified = serializers.BooleanField() 
        