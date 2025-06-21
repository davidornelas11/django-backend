#!/usr/bin/env python3
"""
Cleanup Script for Failed Meal Plans

This script cleans up old failed meal plans and resets them for fresh testing.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/dornela3/Desktop/django-project')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import Profile

def cleanup_failed_plans():
    """Clean up failed meal plans"""
    print("🧹 Cleaning Up Failed Meal Plans")
    print("=" * 50)
    
    # Find failed profiles
    failed_profiles = Profile.objects.filter(status='FAILED')
    
    if not failed_profiles:
        print("✅ No failed profiles to clean up")
        return
    
    print(f"Found {failed_profiles.count()} failed profiles")
    
    # Delete the users (which will also delete their profiles)
    for profile in failed_profiles:
        print(f"  - Deleting user: {profile.user.username}")
        profile.user.delete()
    
    print("✅ Cleaned up all failed profiles")

def reset_pending_plans():
    """Reset pending plans to try again"""
    print("\n🔄 Resetting Pending Meal Plans")
    print("=" * 50)
    
    # Find pending profiles
    pending_profiles = Profile.objects.filter(status='PENDING')
    
    if not pending_profiles:
        print("✅ No pending profiles to reset")
        return
    
    print(f"Found {pending_profiles.count()} pending profiles")
    
    for profile in pending_profiles:
        print(f"  - Resetting profile for user: {profile.user.username}")
        # Clear any old meal plan data
        profile.meal_plan = None
        profile.status = 'PENDING'
        profile.save()
    
    print("✅ Reset all pending profiles")

def show_current_status():
    """Show current database status"""
    print("\n📊 Current Database Status")
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
            if profile.meal_plan and isinstance(profile.meal_plan, dict):
                plan_text = profile.meal_plan.get('plan', '')
                print(f"  - {profile.user.username}: {len(plan_text)} chars")
            else:
                print(f"  - {profile.user.username}: No meal plan data")

def main():
    """Run cleanup operations"""
    print("🚀 Meal Plan Database Cleanup")
    print("=" * 50)
    
    # Show current status
    show_current_status()
    
    # Ask for confirmation
    print("\n" + "=" * 50)
    response = input("Would you like to clean up failed plans and reset pending ones? (y/n): ")
    
    if response.lower() in ['y', 'yes']:
        cleanup_failed_plans()
        reset_pending_plans()
        
        print("\n" + "=" * 50)
        print("📊 Updated Database Status")
        print("=" * 50)
        show_current_status()
    else:
        print("Cleanup cancelled")

if __name__ == "__main__":
    main() 