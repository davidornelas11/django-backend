#!/usr/bin/env python3
"""
Database Inspection Script for Meal Plans

This script checks the database to see if meal plans are being generated and stored properly.
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import Profile

def check_all_profiles():
    """Check all profiles in the database"""
    print("🔍 Checking All Profiles in Database")
    print("=" * 60)
    
    profiles = Profile.objects.all().order_by('-created_at')
    
    if not profiles:
        print("❌ No profiles found in database")
        return
    
    print(f"📊 Found {profiles.count()} profiles in database")
    print()
    
    for i, profile in enumerate(profiles, 1):
        print(f"Profile #{i}:")
        print(f"  - ID: {profile.id}")
        print(f"  - User: {profile.user.username}")
        print(f"  - Email: {profile.user.email}")
        print(f"  - Email Verified: {profile.is_email_verified}")
        print(f"  - Status: {profile.status}")
        print(f"  - Created: {profile.created_at}")
        print(f"  - Updated: {profile.updated_at}")
        
        if profile.preferences:
            print(f"  - Preferences: {profile.preferences}")
        
        if profile.dietary_restrictions:
            print(f"  - Dietary Restrictions: {profile.dietary_restrictions}")
        
        if profile.weekly_budget:
            print(f"  - Budget: ${profile.weekly_budget}")
        
        if profile.meal_plan:
            print(f"  - ✅ Meal Plan: GENERATED")
            print(f"    - Keys: {list(profile.meal_plan.keys())}")
            if 'plan' in profile.meal_plan:
                plan_text = profile.meal_plan['plan']
                print(f"    - Plan length: {len(plan_text)} characters")
                print(f"    - Plan preview: {plan_text[:200]}...")
            if 'cart_url' in profile.meal_plan:
                print(f"    - Cart URL: {profile.meal_plan['cart_url']}")
        else:
            print(f"  - ❌ Meal Plan: NOT GENERATED")
            if not profile.is_email_verified:
                print(f"    - Reason: Email not verified")
        
        print("-" * 40)

def check_completed_profiles():
    """Check only profiles with completed meal plans"""
    print("\n🔍 Checking Completed Meal Plans")
    print("=" * 60)
    
    completed_profiles = Profile.objects.filter(status='COMPLETED')
    
    if not completed_profiles:
        print("❌ No completed meal plans found")
        return
    
    print(f"✅ Found {completed_profiles.count()} completed meal plans")
    print()
    
    for i, profile in enumerate(completed_profiles, 1):
        print(f"Completed Plan #{i}:")
        print(f"  - User: {profile.user.username}")
        print(f"  - Profile ID: {profile.id}")
        print(f"  - Generated: {profile.updated_at}")
        
        if profile.meal_plan and 'plan' in profile.meal_plan:
            plan_text = profile.meal_plan['plan']
            print(f"  - Plan length: {len(plan_text)} characters")
            
            # Show a better preview of the meal plan
            lines = plan_text.split('\n')
            print("  - Plan preview:")
            for line in lines[:10]:  # Show first 10 lines
                if line.strip():
                    print(f"    {line}")
            if len(lines) > 10:
                print(f"    ... ({len(lines) - 10} more lines)")
        
        if profile.meal_plan and 'cart_url' in profile.meal_plan:
            print(f"  - Cart URL: {profile.meal_plan['cart_url']}")
        
        print("-" * 40)

def check_failed_profiles():
    """Check profiles that failed to generate meal plans"""
    print("\n🔍 Checking Failed Meal Plans")
    print("=" * 60)
    
    failed_profiles = Profile.objects.filter(status='FAILED')
    
    if not failed_profiles:
        print("✅ No failed meal plans found")
        return
    
    print(f"❌ Found {failed_profiles.count()} failed meal plans")
    print()
    
    for i, profile in enumerate(failed_profiles, 1):
        print(f"Failed Plan #{i}:")
        print(f"  - User: {profile.user.username}")
        print(f"  - Profile ID: {profile.id}")
        print(f"  - Last updated: {profile.updated_at}")
        print("-" * 40)

def check_pending_profiles():
    """Check profiles that are still pending"""
    print("\n🔍 Checking Pending Meal Plans")
    print("=" * 60)
    
    pending_profiles = Profile.objects.filter(status='PENDING')
    
    if not pending_profiles:
        print("✅ No pending meal plans found")
        return
    
    print(f"⏳ Found {pending_profiles.count()} pending meal plans")
    print()
    
    for i, profile in enumerate(pending_profiles, 1):
        print(f"Pending Plan #{i}:")
        print(f"  - User: {profile.user.username}")
        print(f"  - Profile ID: {profile.id}")
        print(f"  - Created: {profile.created_at}")
        print(f"  - Last updated: {profile.updated_at}")
        print("-" * 40)

def check_recent_activity():
    """Check recent activity in the last hour"""
    print("\n🔍 Checking Recent Activity (Last Hour)")
    print("=" * 60)
    
    from django.utils import timezone
    from datetime import timedelta
    
    one_hour_ago = timezone.now() - timedelta(hours=1)
    recent_profiles = Profile.objects.filter(updated_at__gte=one_hour_ago).order_by('-updated_at')
    
    if not recent_profiles:
        print("⏰ No recent activity in the last hour")
        return
    
    print(f"🕐 Found {recent_profiles.count()} profiles updated in the last hour")
    print()
    
    for profile in recent_profiles:
        print(f"Recent Activity:")
        print(f"  - User: {profile.user.username}")
        print(f"  - Profile ID: {profile.id}")
        print(f"  - Status: {profile.status}")
        print(f"  - Updated: {profile.updated_at}")
        print(f"  - Time ago: {timezone.now() - profile.updated_at}")
        print("-" * 40)

def create_test_meal_plan():
    """Create a test meal plan to verify the system works"""
    print("\n🔍 Creating Test Meal Plan")
    print("=" * 60)
    
    try:
        # Create a test user
        test_username = f"test_inspect_{int(datetime.now().timestamp())}"
        test_user = User.objects.create_user(
            username=test_username,
            email=f"{test_username}@test.com",
            password="testpass123"
        )
        
        # Set up profile
        profile = test_user.profile
        profile.preferences = {
            "cuisines": ["Italian", "Mexican"],
            "cooking_skill": "beginner"
        }
        profile.dietary_restrictions = {
            "vegetarian": False,
            "allergies": []
        }
        profile.weekly_budget = 100.00
        profile.latitude = 37.7749
        profile.longitude = -122.4194
        profile.preferred_store_id = "test_store_123"
        profile.save()
        
        print(f"✅ Created test profile:")
        print(f"  - User: {test_user.username}")
        print(f"  - Profile ID: {profile.id}")
        print(f"  - Status: {profile.status}")
        print(f"  - Email verified: {profile.is_email_verified}")
        
        # Verify email for meal plan creation
        from users.models import EmailVerification
        verification = test_user.email_verification
        verification.is_verified = True
        verification.save()
        
        # Refresh profile to show updated verification status
        profile.refresh_from_db()
        print(f"  - Email verified after update: {profile.is_email_verified}")
        
        # Trigger meal plan generation
        from core.tasks import generate_meal_plan
        from celery.result import AsyncResult
        
        print(f"🚀 Triggering meal plan generation...")
        task = generate_meal_plan.delay(profile.id)
        print(f"  - Task ID: {task.id}")
        
        # Wait for completion
        import time
        timeout = 120  # 2 minutes
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = AsyncResult(task.id)
            if result.ready():
                if result.successful():
                    print("✅ Task completed successfully")
                    
                    # Refresh profile from database
                    profile.refresh_from_db()
                    
                    if profile.status == 'COMPLETED' and profile.meal_plan:
                        print("✅ Meal plan generated and stored!")
                        print(f"  - Status: {profile.status}")
                        print(f"  - Meal plan keys: {list(profile.meal_plan.keys())}")
                        
                        if 'plan' in profile.meal_plan:
                            plan_text = profile.meal_plan['plan']
                            print(f"  - Plan length: {len(plan_text)} characters")
                            print(f"  - Plan preview: {plan_text[:300]}...")
                        
                        if 'cart_url' in profile.meal_plan:
                            print(f"  - Cart URL: {profile.meal_plan['cart_url']}")
                        
                        # Clean up test user
                        test_user.delete()
                        return True
                    else:
                        print(f"❌ Profile not updated correctly. Status: {profile.status}")
                        test_user.delete()
                        return False
                else:
                    print(f"❌ Task failed: {result.result}")
                    test_user.delete()
                    return False
            
            time.sleep(5)
            print(f"  - Still processing... ({int(time.time() - start_time)}s elapsed)")
        
        print("❌ Task timed out")
        test_user.delete()
        return False
        
    except Exception as e:
        print(f"❌ Error creating test meal plan: {str(e)}")
        if 'test_user' in locals():
            test_user.delete()
        return False

def main():
    """Run all checks"""
    print("🚀 Meal Plan Database Inspection")
    print("=" * 60)
    
    # Run all checks
    check_all_profiles()
    check_completed_profiles()
    check_failed_profiles()
    check_pending_profiles()
    check_recent_activity()
    
    # Ask if user wants to create a test meal plan
    print("\n" + "=" * 60)
    print("🧪 Test Meal Plan Generation")
    print("=" * 60)
    
    response = input("Would you like to create a test meal plan to verify the system works? (y/n): ")
    if response.lower() in ['y', 'yes']:
        create_test_meal_plan()

if __name__ == "__main__":
    main() 