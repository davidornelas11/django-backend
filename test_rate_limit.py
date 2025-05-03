import requests
import time

BASE_URL = 'http://127.0.0.1:8000'

def test_registration_rate_limit():
    print("\nTesting Registration Rate Limit (5 attempts per hour)...")
    
    for i in range(6):  # Try 6 times (should fail on 6th attempt)
        data = {
            'username': f'testuser{i}',
            'password': 'TestPass123!',
            'email': f'test{i}@example.com'
        }
        
        response = requests.post(f'{BASE_URL}/auth/register/', json=data)
        print(f"\nAttempt {i+1}:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 429:  # Too Many Requests
            print("Rate limit hit! Need to wait before trying again.")
            break
        
        time.sleep(1)  # Small delay between requests

def test_login_rate_limit():
    print("\nTesting Login Rate Limit (5 attempts per minute)...")
    
    # First create a user
    user_data = {
        'username': 'ratelimituser',
        'password': 'TestPass123!',
        'email': 'ratelimit@example.com'
    }
    requests.post(f'{BASE_URL}/auth/register/', json=user_data)
    
    # Try to login multiple times
    for i in range(10):  # (should fail after 5 attempts)
        data = {
            'username': 'ratelimituser',
            'password': 'TestPass123!'
        }
        
        response = requests.post(f'{BASE_URL}/auth/login/', json=data)
        print(f"\nLogin Attempt {i+1}:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 429:
            print("Rate limit hit! Need to wait before trying again.")
            break
        
        time.sleep(0.5)  # Reduced delay between requests

if __name__ == '__main__':
    print("Starting Rate Limit Tests...")
    test_registration_rate_limit()
    test_login_rate_limit() 