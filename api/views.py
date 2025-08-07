from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from core.tasks import generate_meal_plan

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def trigger_meal_plan_view(request):
    """
    Trigger the meal planning and Instacart cart creation process.
    Accepts meal planning data directly from the request body.
    
    Args:
        request: The HTTP request object containing meal planning preferences
    """
    try:
        # Get meal planning data from request body
        meal_data = request.data
        
        # Validate required fields
        required_fields = ['preferences', 'dietary_restrictions', 'budget']
        for field in required_fields:
            if field not in meal_data:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }, status=400)
        
        # Trigger the async task with the meal data
        task = generate_meal_plan.delay(meal_data)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Meal planning process initiated',
            'task_id': task.id
        })
    except Exception as e:
        import logging
        logging.error("Error initiating meal planning process: %s", str(e), exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': 'An internal error occurred while initiating the meal planning process.'
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def check_email_verification_status(request):
    """
    Check if the current user's email is verified.
    """
    return Response({
        'email_verified': request.user.profile.is_email_verified,
        'email': request.user.email,
        'username': request.user.username
    })
