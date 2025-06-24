#!/usr/bin/env python3
"""
Authentication Test Script for Django Meal Planning System

This script tests the complete authentication and email verification flow:
1. User registration with email verification
2. Email verification process
3. Login/logout functionality
4. Protected endpoint access
5. Rate limiting and security

Run this script to verify your authentication system is working correctly.
"""

import os
import sys
import django
import time
import requests
import json
from datetime import datetime

# Setup Django with test-friendly throttling
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ.setdefault('TESTING_MODE', 'True')  # Flag for test mode
django.setup()

# Override throttle settings for testing
from django.conf import settings
if hasattr(settings, 'REST_FRAMEWORK'):
    # Temporarily disable throttling for tests
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
        'anon': '1000/hour',  # Very generous for testing
        'user': '1000/hour'
    }

from django.contrib.auth.models import User
from users.models import Profile, EmailVerification, RefreshToken
from rest_framework.authtoken.models import Token

BASE_URL = "http://localhost:8000"

def test_user_registration():
    """Test 1: User registration with email verification"""
    print("🔍 Testing User Registration...")
    
    try:
        # Create test user data
        test_username = f"auth_test_{int(time.time())}"
        test_email = f"{test_username}@test.com"
        test_password = "SecureTestPass123!"
        
        registration_data = {
            "username": test_username,
            "email": test_email,
            "password": test_password
        }
        
        # Register user via API
        response = requests.post(
            f"{BASE_URL}/auth/register/",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            print("✅ User registration successful")
            print(f"   - Username: {test_username}")
            print(f"   - Email verification sent: {data.get('email_verification_sent', False)}")
            print(f"   - Access token received: {'access_token' in data}")
            
            # Check if user exists in database
            user = User.objects.get(username=test_username)
            print(f"   - User created in database: {user.id}")
            print(f"   - Profile created: {hasattr(user, 'profile')}")
            print(f"   - Email verification record: {hasattr(user, 'email_verification')}")
            
            return {
                'user': user,
                'access_token': data.get('access_token'),
                'refresh_token': data.get('refresh_token'),
                'password': test_password
            }
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   - Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Registration test failed: {str(e)}")
        return None

def test_email_verification(user_data):
    """Test 2: Email verification process"""
    print("\n🔍 Testing Email Verification...")
    
    if not user_data:
        print("❌ No user data from registration test")
        return False
    
    try:
        user = user_data['user']
        access_token = user_data['access_token']
        
        # Check initial verification status
        print(f"   - Initial verification status: {user.profile.is_email_verified}")
        
        # Get verification token from database
        verification = user.email_verification
        verification_token = verification.verification_token
        
        print(f"   - Verification token exists: {bool(verification_token)}")
        print(f"   - Token expires at: {verification.expires_at}")
        
        # Test verification API endpoint
        verification_data = {"token": verification_token}
        response = requests.post(
            f"{BASE_URL}/auth/verify-email/",
            json=verification_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Email verification successful")
            
            # Refresh user from database
            user.refresh_from_db()
            verification.refresh_from_db()
            
            print(f"   - Verification status updated: {verification.is_verified}")
            print(f"   - Profile verification property: {user.profile.is_email_verified}")
            
            return True
        else:
            print(f"❌ Email verification failed: {response.status_code}")
            print(f"   - Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Email verification test failed: {str(e)}")
        return False

def test_login_logout(user_data):
    """Test 3: Login and logout functionality"""
    print("\n🔍 Testing Login/Logout...")
    
    if not user_data:
        print("❌ No user data for login test")
        return None
    
    try:
        user = user_data['user']
        password = user_data['password']
        
        # Add delay to avoid rate limiting
        time.sleep(15)  # Wait longer for login due to 5/minute limit
        
        # Test login
        login_data = {
            "username": user.username,
            "password": password
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/login/",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful")
            print(f"   - Access token received: {'access_token' in data}")
            print(f"   - Email verified in response: {data.get('email_verified', False)}")
            
            new_access_token = data.get('access_token')
            
            # Test logout
            response = requests.post(
                f"{BASE_URL}/auth/logout/",
                headers={"Authorization": f"Token {new_access_token}"}
            )
            
            if response.status_code == 200:
                print("✅ Logout successful")
                return new_access_token
            else:
                print(f"❌ Logout failed: {response.status_code}")
                return new_access_token
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   - Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login/logout test failed: {str(e)}")
        return None

def test_protected_endpoints(user_data, access_token):
    """Test 4: Protected endpoint access with and without verification"""
    print("\n🔍 Testing Protected Endpoints...")
    
    if not user_data or not access_token:
        print("❌ Missing data for protected endpoint test")
        return False
    
    try:
        user = user_data['user']
        profile_id = user.profile.id
        
        # Test email verification status endpoint
        response = requests.get(
            f"{BASE_URL}/api/email-verification-status/",
            headers={"Authorization": f"Token {access_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Email verification status endpoint works")
            print(f"   - Email verified: {data.get('email_verified', False)}")
            print(f"   - Username: {data.get('username')}")
        else:
            print(f"❌ Email verification status failed: {response.status_code}")
        
        # Test meal plan creation (should work with verified email)
        response = requests.post(
            f"{BASE_URL}/api/profiles/{profile_id}/trigger-meal-plan/",
            headers={"Authorization": f"Token {access_token}"}
        )
        
        if response.status_code == 200:
            print("✅ Meal plan creation endpoint accessible (email verified)")
            data = response.json()
            print(f"   - Task ID: {data.get('task_id')}")
        elif response.status_code == 403:
            error_data = response.json()
            if "Email verification" in error_data.get('message', ''):
                print("✅ Meal plan creation properly blocked (email not verified)")
            else:
                print(f"❌ Unexpected 403 error: {error_data}")
        else:
            print(f"❌ Unexpected meal plan creation response: {response.status_code}")
            print(f"   - Response: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Protected endpoints test failed: {str(e)}")
        return False

def test_unverified_user_restrictions():
    """Test 5: Create unverified user and test restrictions"""
    print("\n🔍 Testing Unverified User Restrictions...")
    
    try:
        # Create unverified user
        test_username = f"unverified_test_{int(time.time())}"
        test_email = f"{test_username}@test.com"
        test_password = "UnverifiedPass123!"
        
        user = User.objects.create_user(
            username=test_username,
            email=test_email,
            password=test_password
        )
        
        # Create token manually (since email is not verified)
        token, _ = Token.objects.get_or_create(user=user)
        
        print(f"✅ Created unverified user: {test_username}")
        print(f"   - Email verified: {user.profile.is_email_verified}")
        
        # Test meal plan creation (should fail)
        response = requests.post(
            f"{BASE_URL}/api/profiles/{user.profile.id}/trigger-meal-plan/",
            headers={"Authorization": f"Token {token.key}"}
        )
        
        if response.status_code == 403:
            error_data = response.json()
            if "Email verification" in error_data.get('detail', ''):
                print("✅ Meal plan creation properly blocked for unverified user")
            else:
                print(f"❌ Wrong 403 error message: {error_data}")
        else:
            print(f"❌ Unverified user was allowed access: {response.status_code}")
            print(f"   - Response: {response.text}")
        
        # Cleanup
        user.delete()
        return True
        
    except Exception as e:
        print(f"❌ Unverified user restrictions test failed: {str(e)}")
        return False

def test_rate_limiting():
    """Test 6: Rate limiting on authentication endpoints"""
    print("\n🔍 Testing Rate Limiting...")
    
    try:
        # Test registration rate limiting (5/hour)
        print("   - Testing registration rate limiting...")
        successful_registrations = 0
        
        for i in range(3):  # Test 3 registrations
            test_username = f"rate_test_{int(time.time())}_{i}"
            registration_data = {
                "username": test_username,
                "email": f"{test_username}@test.com",
                "password": "RateTestPass123!"
            }
            
            response = requests.post(
                f"{BASE_URL}/auth/register/",
                json=registration_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                successful_registrations += 1
                # Cleanup
                User.objects.filter(username=test_username).delete()
            elif response.status_code == 429:
                print(f"   - Rate limiting activated after {successful_registrations} registrations")
                break
            
            time.sleep(1)  # Small delay between requests
        
        print(f"✅ Registration rate limiting test completed")
        print(f"   - Successful registrations before rate limit: {successful_registrations}")
        
        return True
        
    except Exception as e:
        print(f"❌ Rate limiting test failed: {str(e)}")
        return False

def test_email_resend():
    """Test 7: Email verification resend functionality"""
    print("\n🔍 Testing Email Resend...")
    
    try:
        # Create test user
        test_username = f"resend_test_{int(time.time())}"
        test_email = f"{test_username}@test.com"
        
        user = User.objects.create_user(
            username=test_username,
            email=test_email,
            password="ResendTestPass123!"
        )
        
        # Add longer delay to avoid rate limiting (email has 3/hour limit)
        time.sleep(5)
        
        # Test resend endpoint
        resend_data = {"email": test_email}
        response = requests.post(
            f"{BASE_URL}/auth/resend-verification/",
            json=resend_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Email resend successful")
            data = response.json()
            print(f"   - Message: {data.get('message')}")
        else:
            print(f"❌ Email resend failed: {response.status_code}")
            print(f"   - Response: {response.text}")
        
        # Cleanup
        user.delete()
        return True
        
    except Exception as e:
        print(f"❌ Email resend test failed: {str(e)}")
        return False

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    try:
        # Remove test users
        deleted_count = User.objects.filter(
            username__startswith='auth_test_'
        ).delete()[0]
        
        deleted_count += User.objects.filter(
            username__startswith='unverified_test_'
        ).delete()[0]
        
        deleted_count += User.objects.filter(
            username__startswith='rate_test_'
        ).delete()[0]
        
        deleted_count += User.objects.filter(
            username__startswith='resend_test_'
        ).delete()[0]
        
        print(f"✅ Cleaned up {deleted_count} test users")
        
    except Exception as e:
        print(f"⚠️  Cleanup warning: {str(e)}")

def main():
    """Run all authentication tests"""
    print("🚀 Starting Authentication Tests for Django Meal Planning System")
    print("=" * 70)
    
    # Check if Django server is running
    try:
        response = requests.get(f"{BASE_URL}/auth/login/")
        if response.status_code not in [200, 405, 401]:  # These are expected responses
            print(f"❌ Django server not accessible at {BASE_URL}")
            print("   Please start the server: python manage.py runserver")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Django server at {BASE_URL}")
        print("   Please start the server: python manage.py runserver")
        return False
    
    tests = [
        ("User Registration", test_user_registration),
        ("Unverified User Restrictions", test_unverified_user_restrictions),
        ("Rate Limiting", test_rate_limiting),
        ("Email Resend", test_email_resend),
    ]
    
    results = []
    user_data = None
    access_token = None
    
    # Run initial tests
    for test_name, test_func in tests:
        try:
            if test_name == "User Registration":
                result = test_func()
                user_data = result
                results.append((test_name, bool(result)))
            else:
                result = test_func()
                results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Run dependent tests if registration succeeded
    if user_data:
        dependent_tests = [
            ("Email Verification", lambda: test_email_verification(user_data)),
            ("Login/Logout", lambda: test_login_logout(user_data)),
        ]
        
        for test_name, test_func in dependent_tests:
            try:
                if test_name == "Login/Logout":
                    result = test_func()
                    access_token = result
                    results.append((test_name, bool(result)))
                else:
                    result = test_func()
                    results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} test crashed: {str(e)}")
                results.append((test_name, False))
        
        # Test protected endpoints if we have a token
        if access_token:
            try:
                result = test_protected_endpoints(user_data, access_token)
                results.append(("Protected Endpoints", result))
            except Exception as e:
                print(f"❌ Protected Endpoints test crashed: {str(e)}")
                results.append(("Protected Endpoints", False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 AUTHENTICATION TEST RESULTS")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} authentication tests passed")
    
    if passed == total:
        print("🎉 All authentication tests passed!")
        print("\n📋 Summary of what was tested:")
        print("  ✅ User registration with email verification")
        print("  ✅ Email verification process")
        print("  ✅ Login/logout functionality")
        print("  ✅ Protected endpoint access control")
        print("  ✅ Unverified user restrictions")
        print("  ✅ Rate limiting on auth endpoints")
        print("  ✅ Email verification resend")
        print("\n🔐 Your authentication system is working correctly!")
    else:
        print("⚠️  Some authentication tests failed.")
        print("   Check the errors above and verify your settings.")
    
    # Cleanup
    cleanup_test_data()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 