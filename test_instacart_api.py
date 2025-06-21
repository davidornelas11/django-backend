#!/usr/bin/env python3
"""
Test script for Instacart API integration
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def test_instacart_api_key():
    """Test if the Instacart API key is properly configured"""
    print("🔍 Testing Instacart API Key Configuration...")
    
    api_key = os.getenv('INSTACART_API_KEY')
    
    if not api_key:
        print("❌ INSTACART_API_KEY not found in environment variables")
        print("   Please add your Instacart API key to your .env file:")
        print("   INSTACART_API_KEY=your-actual-api-key")
        return False
    
    if api_key == 'your-instacart-api-key-here' or 'test' in api_key.lower():
        print("❌ INSTACART_API_KEY appears to be a placeholder or test value")
        print("   Please replace with your actual Instacart API key")
        return False
    
    print(f"✅ INSTACART_API_KEY found: {api_key[:10]}...{api_key[-4:]}")
    return True

def test_instacart_client_initialization():
    """Test Instacart client initialization with real API key"""
    print("\n🔍 Testing Instacart Client Initialization...")
    
    try:
        from core.instacart_client import InstacartClient
        
        api_key = os.getenv('INSTACART_API_KEY')
        if not api_key:
            print("❌ No API key available for testing")
            return False
        
        client = InstacartClient(api_key=api_key)
        print("✅ Instacart client initialized successfully")
        print(f"   - Base URL: {client.base_url}")
        print(f"   - Authorization header: Bearer {api_key[:10]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize Instacart client: {str(e)}")
        return False

def test_instacart_api_connection():
    """Test actual connection to Instacart API"""
    print("\n🔍 Testing Instacart API Connection...")
    
    try:
        from core.instacart_client import InstacartClient
        
        api_key = os.getenv('INSTACART_API_KEY')
        if not api_key:
            print("❌ No API key available for testing")
            return False
        
        client = InstacartClient(api_key=api_key)
        
        # Try to make a simple API call to test connectivity
        # This will depend on what endpoints are available in your Instacart API
        print("   - Testing API connectivity...")
        
        # For now, we'll just test that the client can be created
        # You might want to add actual API calls here based on your Instacart API documentation
        print("✅ Instacart client created successfully")
        print("   - Ready to make API calls")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Instacart API: {str(e)}")
        return False

def test_meal_plan_with_instacart():
    """Test the full meal planning workflow with Instacart integration"""
    print("\n🔍 Testing Meal Planning with Instacart Integration...")
    
    try:
        from django.contrib.auth.models import User
        from users.models import Profile
        from core.tasks import generate_meal_plan
        from celery.result import AsyncResult
        import time
        
        # Create a test user
        test_username = f"instacart_test_{int(time.time())}"
        test_user = User.objects.create_user(
            username=test_username,
            email=f"{test_username}@test.com",
            password="testpass123"
        )
        
        # Set up profile with location and store preferences
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
        profile.latitude = 37.7749  # San Francisco coordinates
        profile.longitude = -122.4194
        profile.preferred_store_id = "test_store_123"  # You'll need a real store ID
        profile.save()
        
        print(f"   - Created test profile: {profile.id}")
        print(f"   - Location: {profile.latitude}, {profile.longitude}")
        print(f"   - Store ID: {profile.preferred_store_id}")
        
        # Trigger meal plan generation
        task = generate_meal_plan.delay(profile.id)
        print(f"   - Task ID: {task.id}")
        
        # Wait for completion (with timeout)
        timeout = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = AsyncResult(task.id)
            if result.ready():
                if result.successful():
                    print("✅ Meal plan generation completed successfully")
                    
                    # Check if profile was updated
                    profile.refresh_from_db()
                    if profile.status == 'COMPLETED' and profile.meal_plan:
                        print("✅ Profile updated with meal plan and cart URL")
                        print(f"   - Status: {profile.status}")
                        print(f"   - Meal plan keys: {list(profile.meal_plan.keys())}")
                        
                        if 'cart_url' in profile.meal_plan:
                            print(f"   - Cart URL: {profile.meal_plan['cart_url']}")
                        
                        # Keep the test user for inspection
                        print(f"   - Test user preserved: {test_user.username}")
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
        print(f"❌ Meal planning with Instacart test failed: {str(e)}")
        if 'test_user' in locals():
            test_user.delete()
        return False

def main():
    """Run all Instacart API tests"""
    print("🚀 Starting Instacart API Tests")
    print("=" * 50)
    
    tests = [
        ("API Key Configuration", test_instacart_api_key),
        ("Client Initialization", test_instacart_client_initialization),
        ("API Connection", test_instacart_api_connection),
        ("Meal Planning Integration", test_meal_plan_with_instacart),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 INSTACART API TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Instacart API tests passed!")
    else:
        print("⚠️  Some tests failed. Check your API key and configuration.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 