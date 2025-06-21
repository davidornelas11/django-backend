#!/usr/bin/env python3
"""
Unit Test Script for Django Meal Planning Components

This script tests individual components separately:
1. LangChain setup
2. OpenAI connection
3. Instacart client
4. Database models
5. Celery configuration

Run individual test functions to debug specific issues.
"""

import os
import sys
import django
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def test_langchain_setup():
    """Test LangChain dependencies and setup"""
    print("🔍 Testing LangChain Setup...")
    
    try:
        from langchain.chat_models import ChatOpenAI
        from langchain.prompts import PromptTemplate
        from langchain.chains import LLMChain
        
        print("✅ All LangChain imports successful")
        
        # Test OpenAI model initialization
        llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-4o-mini",  # Use a valid model name
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        print("✅ OpenAI model initialized")
        
        # Test prompt template
        template = "Test template with {input}"
        prompt = PromptTemplate(template=template, input_variables=["input"])
        print("✅ Prompt template created")
        
        # Test LLMChain
        chain = LLMChain(llm=llm, prompt=prompt)
        print("✅ LLMChain created")
        
        return True
        
    except Exception as e:
        print(f"❌ LangChain setup failed: {str(e)}")
        return False

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n🔍 Testing OpenAI Connection...")
    
    try:
        from langchain.chat_models import ChatOpenAI
        
        llm = ChatOpenAI(
            temperature=0.1,
            model_name="gpt-4o-mini",
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Test a simple completion
        response = llm.invoke("Say 'Hello, World!' in one word.")
        print(f"✅ OpenAI connection successful")
        print(f"   - Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI connection failed: {str(e)}")
        return False

def test_instacart_client_structure():
    """Test Instacart client structure (without API calls)"""
    print("\n🔍 Testing Instacart Client Structure...")
    
    try:
        from core.instacart_client import InstacartClient, Cart
        
        # Test client initialization
        client = InstacartClient(
            api_key="test_key"
        )
        
        print("✅ Instacart client initialized")
        print(f"   - Base URL: {client.base_url}")
        print(f"   - Headers: {client.session.headers}")
        
        # Test cart creation (mock)
        cart = Cart(client, "test_cart_id")
        print("✅ Cart object created")
        
        # Test adding items
        cart.add_item("test_item", 1.0, "each")
        print(f"✅ Item added to cart: {cart.items}")
        
        return True
        
    except Exception as e:
        print(f"❌ Instacart client test failed: {str(e)}")
        return False

def test_database_models():
    """Test database models and relationships"""
    print("\n🔍 Testing Database Models...")
    
    try:
        from django.contrib.auth.models import User
        from users.models import Profile
        
        # Test user creation
        test_user = User.objects.create_user(
            username=f"model_test_{int(time.time())}",
            email="test@example.com",
            password="testpass"
        )
        
        # Test profile relationship
        profile = test_user.profile
        print(f"✅ User and profile created")
        print(f"   - User ID: {test_user.id}")
        print(f"   - Profile ID: {profile.id}")
        
        # Test profile fields
        profile.preferences = {"test": "data"}
        profile.dietary_restrictions = {"vegetarian": False}
        profile.weekly_budget = 100.00
        profile.save()
        
        print("✅ Profile fields updated")
        
        # Cleanup
        test_user.delete()
        print("✅ Test user cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Database model test failed: {str(e)}")
        return False

def test_celery_configuration():
    """Test Celery configuration"""
    print("\n🔍 Testing Celery Configuration...")
    
    try:
        from core.celery import app
        
        print("✅ Celery app imported successfully")
        print(f"   - App name: {app.main}")
        
        # Test broker connection
        inspect = app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            print("✅ Celery workers are running")
            print(f"   - Active workers: {len(stats)}")
        else:
            print("⚠️  No Celery workers detected (this is normal if workers aren't running)")
        
        return True
        
    except Exception as e:
        print(f"❌ Celery configuration test failed: {str(e)}")
        return False

def test_meal_planning_chain():
    """Test the meal planning chain creation"""
    print("\n🔍 Testing Meal Planning Chain...")
    
    try:
        from core.tasks import create_meal_planning_chain
        
        # Create the chain
        chain = create_meal_planning_chain()
        print("✅ Meal planning chain created")
        
        # Test chain structure
        print(f"   - Chain type: {type(chain).__name__}")
        print(f"   - LLM model: {chain.llm.model_name}")
        print(f"   - Prompt variables: {chain.prompt.input_variables}")
        
        return True
        
    except Exception as e:
        print(f"❌ Meal planning chain test failed: {str(e)}")
        return False

def test_simple_meal_plan():
    """Test a simple meal plan generation (without Instacart)"""
    print("\n🔍 Testing Simple Meal Plan Generation...")
    
    try:
        from core.tasks import create_meal_planning_chain
        
        # Create test data
        test_preferences = {
            "cuisines": ["Italian", "Mexican"],
            "cooking_skill": "beginner"
        }
        test_restrictions = {
            "vegetarian": False,
            "allergies": []
        }
        test_budget = 100.00
        
        # Create chain
        chain = create_meal_planning_chain()
        
        # Test invocation
        result = chain.invoke({
            "preferences": str(test_preferences),
            "dietary_restrictions": str(test_restrictions),
            "budget": str(test_budget)
        })
        
        print("✅ Meal plan generation successful")
        print(f"   - Result type: {type(result)}")
        print(f"   - Result keys: {list(result.keys())}")
        print(f"   - Text length: {len(result['text'])} characters")
        print(f"   - First 100 chars: {result['text'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple meal plan test failed: {str(e)}")
        return False

def main():
    """Run all component tests"""
    print("🚀 Starting Component Tests")
    print("=" * 50)
    
    tests = [
        ("LangChain Setup", test_langchain_setup),
        ("OpenAI Connection", test_openai_connection),
        ("Instacart Client", test_instacart_client_structure),
        ("Database Models", test_database_models),
        ("Celery Configuration", test_celery_configuration),
        ("Meal Planning Chain", test_meal_planning_chain),
        ("Simple Meal Plan", test_simple_meal_plan),
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
    print("📊 COMPONENT TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} component tests passed")
    
    if passed == total:
        print("🎉 All component tests passed!")
    else:
        print("⚠️  Some component tests failed.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 