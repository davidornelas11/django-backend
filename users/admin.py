from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile, EmailVerification, RefreshToken, MealPlanHistory
import json
from django.utils.html import format_html

# Inline admin for Profile
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        'bio', 'location', 'birth_date', 'status',
        'latitude', 'longitude', 'weekly_budget', 'preferred_store_id',
        'preferences_display', 'dietary_restrictions_display', 'meal_plan_display'
    )
    readonly_fields = ('preferences_display', 'dietary_restrictions_display', 'meal_plan_display')
    
    def preferences_display(self, obj):
        if obj.preferences:
            return json.dumps(obj.preferences, indent=2)
        return "No preferences set"
    preferences_display.short_description = "Preferences (JSON)"
    
    def dietary_restrictions_display(self, obj):
        if obj.dietary_restrictions:
            return json.dumps(obj.dietary_restrictions, indent=2)
        return "No dietary restrictions set"
    dietary_restrictions_display.short_description = "Dietary Restrictions (JSON)"
    
    def meal_plan_display(self, obj):
        if obj.meal_plan:
            return json.dumps(obj.meal_plan, indent=2)
        return "No meal plan generated"
    meal_plan_display.short_description = "Meal Plan (JSON)"

# Extended User Admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_email_verified', 'get_profile_status')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    
    def get_email_verified(self, obj):
        try:
            return obj.email_verification.is_verified
        except:
            return False
    get_email_verified.boolean = True
    get_email_verified.short_description = 'Email Verified'
    
    def get_profile_status(self, obj):
        try:
            return obj.profile.status
        except:
            return 'No Profile'
    get_profile_status.short_description = 'Profile Status'

# Profile Admin
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'weekly_budget', 'location', 'created_at', 'has_meal_plan')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'location')
    readonly_fields = ('created_at', 'updated_at', 'preferences_display', 'dietary_restrictions_display', 'meal_plan_display')
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'status', 'bio', 'location', 'birth_date')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Meal Planning', {
            'fields': ('weekly_budget', 'preferred_store_id', 'preferences_display', 'dietary_restrictions_display')
        }),
        ('Generated Meal Plan', {
            'fields': ('meal_plan_display',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def has_meal_plan(self, obj):
        return bool(obj.meal_plan)
    has_meal_plan.boolean = True
    has_meal_plan.short_description = 'Has Meal Plan'
    
    def preferences_display(self, obj):
        if obj.preferences:
            return json.dumps(obj.preferences, indent=2)
        return "No preferences set"
    preferences_display.short_description = "Preferences (JSON)"
    
    def dietary_restrictions_display(self, obj):
        if obj.dietary_restrictions:
            return json.dumps(obj.dietary_restrictions, indent=2)
        return "No dietary restrictions set"
    dietary_restrictions_display.short_description = "Dietary Restrictions (JSON)"
    
    def meal_plan_display(self, obj):
        if obj.meal_plan:
            return json.dumps(obj.meal_plan, indent=2)
        return "No meal plan generated"
    meal_plan_display.short_description = "Meal Plan (JSON)"

# Email Verification Admin
@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'created_at', 'expires_at', 'is_expired_status')
    list_filter = ('is_verified', 'created_at', 'expires_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('verification_token', 'created_at', 'expires_at', 'is_expired_status')
    
    def is_expired_status(self, obj):
        return obj.is_expired()
    is_expired_status.boolean = True
    is_expired_status.short_description = 'Is Expired'

# Refresh Token Admin
@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_valid', 'created_at', 'expires_at')
    list_filter = ('is_valid', 'created_at', 'expires_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('token', 'created_at', 'expires_at')

# Meal Plan History Admin
@admin.register(MealPlanHistory)
class MealPlanHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'week_start_date', 'week_end_date', 'year', 'month', 'week_number', 'total_budget', 'was_completed', 'user_rating', 'archived_at']
    list_filter = ['year', 'month', 'was_completed', 'user_rating', 'archived_at']
    search_fields = ['user__username', 'user__email', 'notes']
    readonly_fields = ['created_at', 'archived_at', 'year', 'week_number', 'month']
    ordering = ['-week_start_date', '-archived_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'week_start_date', 'week_end_date')
        }),
        ('Meal Plan Data', {
            'fields': ('meal_plan_data_formatted', 'total_budget'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('year', 'month', 'week_number', 'created_at', 'archived_at')
        }),
        ('User Feedback', {
            'fields': ('was_completed', 'user_rating', 'notes')
        }),
    )
    
    def meal_plan_data_formatted(self, obj):
        """Display formatted JSON meal plan data"""
        if obj.meal_plan_data:
            import json
            try:
                formatted_json = json.dumps(obj.meal_plan_data, indent=2, ensure_ascii=False)
                return format_html('<pre style="white-space: pre-wrap; max-height: 400px; overflow-y: auto;">{}</pre>', formatted_json)
            except (TypeError, ValueError):
                return str(obj.meal_plan_data)
        return "No meal plan data"
    
    meal_plan_data_formatted.short_description = "Meal Plan Data"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

# Re-register User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
