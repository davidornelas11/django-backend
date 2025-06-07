from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from core.tasks import generate_meal_plan

# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_meal_plan_view(request, profile_id):
    """
    Trigger the meal planning and Instacart cart creation process for a specific profile.
    
    Args:
        request: The HTTP request object
        profile_id: The ID of the profile to generate the meal plan for
    """
    try:
        # Trigger the async task
        task = generate_meal_plan.delay(profile_id)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Meal planning process initiated for profile ID: {profile_id}',
            'task_id': task.id
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to initiate meal planning process: {str(e)}'
        }, status=500)
