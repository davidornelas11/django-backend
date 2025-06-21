from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta
import uuid

# Create your models here.

class RefreshToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='refresh_token')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return f"Refresh token for {self.user.username}"

    @classmethod
    def create_token(cls, user, days=30):
        token = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(days=days)
        return cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )

class Profile(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Location data
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Meal planning preferences
    preferences = models.JSONField(default=dict, help_text="User's food preferences and favorite cuisines")
    dietary_restrictions = models.JSONField(default=dict, help_text="User's dietary restrictions and allergies")
    weekly_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Weekly grocery budget")
    preferred_store_id = models.CharField(max_length=100, blank=True, help_text="Preferred Instacart store ID")
    
    # Generated meal plan and cart data
    meal_plan = models.JSONField(null=True, blank=True, help_text="Generated meal plan and Instacart cart URL")

    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
