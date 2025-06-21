#!/usr/bin/env python3
"""
Test Celery Task Submission

This script manually submits a Celery task to test if it's being received.
"""

import os
import sys
import django
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.tasks import generate_meal_plan
from celery.result import AsyncResult
from users.models import Profile

def test_task_submission():
    """Test submitting a task to Celery"""
    print("🧪 Testing Celery Task Submission")
    print("=" * 50)
    
    # Create a test profile
    from django.contrib.auth.models import User
    
    test_username = f"celery_test_{int(time.time())}"
    test_user = User.objects.create_user(
        username=test_username,
        email=f"{test_username}@test.com",
        password="testpass123"
    )
    
    profile = test_user.profile
    profile.preferences = {
        "cuisines": ["Italian"],
        "cooking_skill": "beginner"
    }
    profile.dietary_restrictions = {
        "vegetarian": False,
        "allergies": []
    }
    profile.weekly_budget = 50.00
    profile.save()
    
    print(f"✅ Created test profile: {test_username} (ID: {profile.id})")
    
    # Submit the task
    print("🚀 Submitting task to Celery...")
    task = generate_meal_plan.delay(profile.id)
    print(f"✅ Task submitted with ID: {task.id}")
    
    # Check task status immediately
    result = AsyncResult(task.id)
    print(f"📊 Initial task status: {result.state}")
    
    # Wait and check status
    print("⏳ Waiting for task to be picked up...")
    for i in range(10):  # Wait up to 50 seconds
        time.sleep(5)
        result = AsyncResult(task.id)
        print(f"   - Status after {5*(i+1)}s: {result.state}")
        
        if result.ready():
            if result.successful():
                print("✅ Task completed successfully!")
                print(f"   - Result: {result.result}")
                
                # Check if profile was updated
                profile.refresh_from_db()
                print(f"   - Profile status: {profile.status}")
                if profile.meal_plan:
                    print(f"   - Meal plan generated: {len(profile.meal_plan.get('plan', ''))} chars")
                else:
                    print("   - No meal plan data found")
            else:
                print(f"❌ Task failed: {result.result}")
            break
    
    # Clean up
    test_user.delete()
    print("🧹 Test user cleaned up")
    
    return result.successful() if result.ready() else False

if __name__ == "__main__":
    success = test_task_submission()
    print(f"\n🎯 Test result: {'SUCCESS' if success else 'FAILED'}") 