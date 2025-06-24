from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta
import uuid
from django.utils import timezone

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
        
        # Get or create refresh token for user (since it's OneToOne)
        refresh_token, created = cls.objects.get_or_create(
            user=user,
            defaults={
                'token': token,
                'expires_at': expires_at,
                'is_valid': True
            }
        )
        
        # If token already exists, update it with new values
        if not created:
            refresh_token.token = token
            refresh_token.expires_at = expires_at
            refresh_token.is_valid = True
            refresh_token.save()
            
        return refresh_token

class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    verification_token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Email verification for {self.user.username}"
    
    @classmethod
    def create_verification(cls, user):
        """Create a new email verification token"""
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(hours=24)  # 24 hour expiry
        verification, created = cls.objects.get_or_create(
            user=user,
            defaults={
                'verification_token': token,
                'expires_at': expires_at
            }
        )
        if not created:
            # Update existing verification with new token
            verification.verification_token = token
            verification.expires_at = expires_at
            verification.is_verified = False
            verification.save()
        return verification
    
    def is_expired(self):
        """Check if verification token is expired"""
        return timezone.now() > self.expires_at

class MealPlanHistory(models.Model):
    """Store historical meal plans for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_plan_history')
    meal_plan_data = models.JSONField(help_text="Complete meal plan data including meals, shopping list, and nutritional info")
    week_start_date = models.DateField(help_text="Start date of the week this meal plan covers")
    week_end_date = models.DateField(help_text="End date of the week this meal plan covers")
    total_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    archived_at = models.DateTimeField(auto_now_add=True)
    
    # Metadata for easy querying
    year = models.IntegerField(help_text="Year of the meal plan")
    week_number = models.IntegerField(help_text="Week number in the year (1-53)")
    month = models.IntegerField(help_text="Month of the meal plan (1-12)")
    
    # Status tracking
    was_completed = models.BooleanField(default=False, help_text="Whether the user completed this meal plan")
    user_rating = models.IntegerField(null=True, blank=True, help_text="User's rating of this meal plan (1-5)")
    notes = models.TextField(blank=True, help_text="User's notes about this meal plan")
    
    class Meta:
        ordering = ['-week_start_date', '-created_at']
        unique_together = ['user', 'week_start_date']  # One meal plan per user per week
        indexes = [
            models.Index(fields=['user', 'week_start_date']),
            models.Index(fields=['user', 'year', 'month']),
            models.Index(fields=['week_start_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username}'s meal plan for week of {self.week_start_date}"
    
    @classmethod
    def archive_current_meal_plan(cls, user):
        """Archive the user's current meal plan to history"""
        profile = user.profile
        
        if not profile.meal_plan:
            return None
            
        # Extract week information from meal plan
        week_of = profile.meal_plan.get('week_of')
        if not week_of:
            # Fallback to current date if no week_of specified
            from datetime import date
            week_start = date.today()
        else:
            from datetime import datetime
            week_start = datetime.strptime(week_of, '%Y-%m-%d').date()
        
        # Calculate week end (6 days later)
        week_end = week_start + timedelta(days=6)
        
        # Create historical record
        history_entry = cls.objects.create(
            user=user,
            meal_plan_data=profile.meal_plan,
            week_start_date=week_start,
            week_end_date=week_end,
            total_budget=profile.meal_plan.get('total_budget'),
            year=week_start.year,
            week_number=week_start.isocalendar()[1],
            month=week_start.month
        )
        
        return history_entry
    
    def get_meal_count(self):
        """Get total number of meals in this plan"""
        meals = self.meal_plan_data.get('meals', [])
        total = 0
        for day in meals:
            total += len([k for k in day.keys() if k != 'day'])
        return total
    
    def get_shopping_list_items(self):
        """Get number of items in shopping list"""
        shopping_list = self.meal_plan_data.get('shopping_list', [])
        return len(shopping_list)

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
    
    # Current active meal plan
    meal_plan = models.JSONField(null=True, blank=True, help_text="Current active meal plan and Instacart cart URL")

    def __str__(self):
        return f"{self.user.username}'s profile"
    
    @property
    def is_email_verified(self):
        """Check if user's email is verified"""
        try:
            return self.user.email_verification.is_verified
        except EmailVerification.DoesNotExist:
            return False
    
    def archive_current_meal_plan(self):
        """Archive current meal plan and clear it for new one"""
        if self.meal_plan:
            # Archive the current meal plan
            archived = MealPlanHistory.archive_current_meal_plan(self.user)
            
            # Clear current meal plan
            self.meal_plan = None
            self.save()
            
            return archived
        return None
    
    def get_meal_plan_history(self, limit=10):
        """Get user's meal plan history"""
        return self.user.meal_plan_history.all()[:limit]

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        # Create email verification for new users
        EmailVerification.create_verification(instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
