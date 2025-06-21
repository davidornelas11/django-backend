#!/usr/bin/env python3
"""
Service Test Script

Quick script to verify that Redis and Celery are running properly.
"""

import os
import sys
import redis
import time

def test_redis_connection():
    """Test Redis connection"""
    print("🔍 Testing Redis Connection...")
    
    try:
        # Try to connect to Redis
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url)
        
        # Test basic operations
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        r.delete('test_key')
        
        if value == b'test_value':
            print("✅ Redis connection successful")
            print(f"   - URL: {redis_url}")
            return True
        else:
            print("❌ Redis test failed - data not retrieved correctly")
            return False
            
    except Exception as e:
        print(f"❌ Redis connection failed: {str(e)}")
        return False

def test_celery_workers():
    """Test if Celery workers are running"""
    print("\n🔍 Testing Celery Workers...")
    
    try:
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        
        import django
        django.setup()
        
        from core.celery import app
        
        # Check worker status
        inspect = app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            print("✅ Celery workers are running")
            for worker_name, worker_stats in stats.items():
                print(f"   - Worker: {worker_name}")
                print(f"     Active tasks: {len(worker_stats.get('active', []))}")
                print(f"     Processed tasks: {worker_stats.get('total', {}).get('core.tasks.generate_meal_plan', 0)}")
            return True
        else:
            print("❌ No Celery workers detected")
            print("   Make sure to start Celery workers with:")
            print("   celery -A core worker --loglevel=info")
            return False
            
    except Exception as e:
        print(f"❌ Celery worker test failed: {str(e)}")
        return False

def test_simple_task():
    """Test a simple Celery task"""
    print("\n🔍 Testing Simple Celery Task...")
    
    try:
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        
        import django
        django.setup()
        
        from core.tasks import generate_meal_plan
        from celery.result import AsyncResult
        
        # Create a simple test task (this will fail but we can test the task submission)
        print("   - Submitting test task...")
        
        # We'll use a non-existent profile ID to test task submission
        task = generate_meal_plan.delay(99999)  # Non-existent profile
        
        print(f"   - Task submitted with ID: {task.id}")
        
        # Wait a moment for the task to be picked up
        time.sleep(2)
        
        result = AsyncResult(task.id)
        if result.state in ['PENDING', 'STARTED', 'SUCCESS', 'FAILURE']:
            print(f"✅ Task submission successful (State: {result.state})")
            return True
        else:
            print(f"❌ Task submission failed (State: {result.state})")
            return False
            
    except Exception as e:
        print(f"❌ Simple task test failed: {str(e)}")
        return False

def main():
    """Run all service tests"""
    print("🚀 Starting Service Tests")
    print("=" * 40)
    
    tests = [
        ("Redis Connection", test_redis_connection),
        ("Celery Workers", test_celery_workers),
        ("Simple Task", test_simple_task),
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
    print("\n" + "=" * 40)
    print("📊 SERVICE TEST RESULTS")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} service tests passed")
    
    if passed == total:
        print("🎉 All services are running correctly!")
    else:
        print("⚠️  Some services need attention.")
        print("\nTo start services:")
        print("1. Start Redis: brew services start redis")
        print("2. Start Celery: celery -A core worker --loglevel=info")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 