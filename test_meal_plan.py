import os
import django
import sys
import uuid

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import Profile
from core.tasks import generate_meal_plan

def create_test_profile():
    """Create a test user and profile with meal planning preferences."""
    # Generate a unique username
    username = f'testuser_{uuid.uuid4().hex[:8]}'
    
    # Create test user (this will automatically create a profile)
    user = User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password='testpass123'
    )
    
    # Get the automatically created profile and update it
    profile = user.profile
    profile.location = 'San Francisco, CA'
    profile.latitude = 37.7749
    profile.longitude = -122.4194
    profile.preferences = {
        'cuisines': ['italian', 'mexican', 'asian'],
        'dislikes': ['seafood', 'spicy'],
        'cooking_level': 'intermediate',
        'meals_per_day': 3,
        'snacks': True
    }
    profile.dietary_restrictions = {
        'vegetarian': True,
        'gluten_free': False,
        'dairy_free': False,
        'allergies': ['nuts']
    }
    profile.weekly_budget = 200.00
    profile.preferred_store_id = 'safeway-123'  # Example store ID
    profile.save()
    
    return profile

def test_meal_planning():
    """Test the meal planning functionality."""
    try:
        # Create test profile
        profile = create_test_profile()
        print(f"Created test profile with ID: {profile.id}")
        print(f"Username: {profile.user.username}")
        print(f"Email: {profile.user.email}")
        
        # Trigger meal planning task
        task = generate_meal_plan.delay(profile.id)
        print(f"Triggered meal planning task with ID: {task.id}")
        
        # Wait for task completion (in a real scenario, you'd use Celery's task monitoring)
        print("Task is running asynchronously. Check the Celery worker logs for progress.")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == '__main__':
    test_meal_planning() 