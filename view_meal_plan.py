#!/usr/bin/env python3
"""
View Meal Plan Content

This script displays the full content of generated meal plans.
"""

import os
import sys
import django
import time

# Add the project directory to Python path
sys.path.append('/Users/dornela3/Desktop/django-project')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import Profile
from django.contrib.auth.models import User

def view_all_meal_plans():
    """View all completed meal plans"""
    print("🍽️  Viewing All Generated Meal Plans")
    print("=" * 80)
    
    completed_profiles = Profile.objects.filter(status='COMPLETED')
    
    if not completed_profiles:
        print("❌ No completed meal plans found")
        return
    
    for i, profile in enumerate(completed_profiles, 1):
        print(f"\n📋 Meal Plan #{i}")
        print(f"User: {profile.user.username}")
        print(f"Profile ID: {profile.id}")
        print(f"Generated: {profile.updated_at}")
        print("=" * 80)
        
        if profile.meal_plan and isinstance(profile.meal_plan, dict) and 'plan' in profile.meal_plan:
            plan_text = profile.meal_plan['plan']
            print(plan_text)
            
            if 'cart_url' in profile.meal_plan:
                print(f"\n🛒 Cart URL: {profile.meal_plan['cart_url']}")
        else:
            print("❌ No meal plan content found")
            print("   This profile was completed but doesn't have meal plan data.")
            print("   This might be from an older version of the system.")
        
        print("\n" + "=" * 80)

def view_specific_meal_plan(profile_id):
    """View a specific meal plan by profile ID"""
    try:
        profile = Profile.objects.get(id=profile_id)
        
        print(f"🍽️  Meal Plan for Profile #{profile_id}")
        print(f"User: {profile.user.username}")
        print(f"Status: {profile.status}")
        print("=" * 80)
        
        if profile.status == 'COMPLETED' and profile.meal_plan:
            if isinstance(profile.meal_plan, dict) and 'plan' in profile.meal_plan:
                print(profile.meal_plan['plan'])
                
                if 'cart_url' in profile.meal_plan:
                    print(f"\n🛒 Cart URL: {profile.meal_plan['cart_url']}")
            else:
                print("❌ No meal plan content found")
        else:
            print(f"❌ No completed meal plan found. Status: {profile.status}")
            
    except Profile.DoesNotExist:
        print(f"❌ Profile #{profile_id} not found")

def create_and_view_meal_plan():
    """Create a new meal plan and view it"""
    print("🚀 Creating New Test Meal Plan")
    print("=" * 80)
    
    try:
        # Create a test user
        test_username = f"view_test_{int(time.time())}"
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
        
        print(f"✅ Created test profile: {test_username} (ID: {profile.id})")
        
        # Trigger meal plan generation
        from core.tasks import generate_meal_plan
        from celery.result import AsyncResult
        
        print("🚀 Triggering meal plan generation...")
        task = generate_meal_plan.delay(profile.id)
        print(f"   - Task ID: {task.id}")
        
        # Wait for completion
        timeout = 120  # 2 minutes
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = AsyncResult(task.id)
            if result.ready():
                if result.successful():
                    print("✅ Task completed successfully!")
                    
                    # Refresh profile from database
                    profile.refresh_from_db()
                    
                    if profile.status == 'COMPLETED' and profile.meal_plan:
                        print("✅ Meal plan generated and stored!")
                        print(f"   - Status: {profile.status}")
                        print(f"   - Meal plan keys: {list(profile.meal_plan.keys())}")
                        
                        # Display the meal plan
                        print("\n" + "=" * 80)
                        print("🍽️  GENERATED MEAL PLAN")
                        print("=" * 80)
                        
                        if 'plan' in profile.meal_plan:
                            plan_text = profile.meal_plan['plan']
                            print(plan_text)
                        
                        if 'cart_url' in profile.meal_plan:
                            print(f"\n🛒 Cart URL: {profile.meal_plan['cart_url']}")
                        
                        print("\n" + "=" * 80)
                        
                        # Ask if user wants to keep this profile
                        response = input("\nWould you like to keep this test profile? (y/n): ")
                        if response.lower() not in ['y', 'yes']:
                            test_user.delete()
                            print("🧹 Test user cleaned up")
                        else:
                            print("✅ Test user kept in database")
                        
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
            print(f"   - Still processing... ({int(time.time() - start_time)}s elapsed)")
        
        print("❌ Task timed out")
        test_user.delete()
        return False
        
    except Exception as e:
        print(f"❌ Error creating test meal plan: {str(e)}")
        if 'test_user' in locals():
            test_user.delete()
        return False

def show_database_status():
    """Show current database status"""
    print("📊 Current Database Status")
    print("=" * 50)
    
    total_profiles = Profile.objects.count()
    completed_profiles = Profile.objects.filter(status='COMPLETED').count()
    pending_profiles = Profile.objects.filter(status='PENDING').count()
    failed_profiles = Profile.objects.filter(status='FAILED').count()
    
    print(f"Total Profiles: {total_profiles}")
    print(f"Completed: {completed_profiles}")
    print(f"Pending: {pending_profiles}")
    print(f"Failed: {failed_profiles}")
    
    # Show completed plans with meal data
    completed = Profile.objects.filter(status='COMPLETED')
    if completed:
        print(f"\n✅ Completed Meal Plans:")
        for profile in completed:
            if profile.meal_plan and isinstance(profile.meal_plan, dict) and 'plan' in profile.meal_plan:
                plan_text = profile.meal_plan['plan']
                print(f"  - {profile.user.username} (ID: {profile.id}): {len(plan_text)} chars")
            else:
                print(f"  - {profile.user.username} (ID: {profile.id}): No meal plan data")

def main():
    """Main function"""
    print("🍽️  Meal Plan Viewer")
    print("=" * 50)
    
    # Show current status first
    show_database_status()
    
    print("\n" + "=" * 50)
    print("Options:")
    print("1. View all completed meal plans")
    print("2. View specific meal plan by profile ID")
    print("3. Create and view a new test meal plan")
    
    choice = input("\nEnter your choice (1, 2, or 3): ")
    
    if choice == "1":
        view_all_meal_plans()
    elif choice == "2":
        profile_id = input("Enter profile ID: ")
        try:
            view_specific_meal_plan(int(profile_id))
        except ValueError:
            print("❌ Invalid profile ID")
    elif choice == "3":
        create_and_view_meal_plan()
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 