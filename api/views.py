from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework import status
from core.tasks import generate_meal_plan

# Create your views here.

class IsEmailVerified(BasePermission):
    """
    Custom permission to only allow access to users with verified email addresses.
    """
    message = "Email verification is required to create meal plans."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.is_email_verified
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEmailVerified])
def trigger_meal_plan_view(request, profile_id):
    """
    Trigger the meal planning and Instacart cart creation process for a specific profile.
    Only authenticated users with verified email addresses can create meal plans.
    
    Args:
        request: The HTTP request object
        profile_id: The ID of the profile to generate the meal plan for
    """
    try:
        # Ensure user can only create meal plans for their own profile
        if request.user.profile.id != profile_id:
            return JsonResponse({
                'status': 'error',
                'message': 'You can only create meal plans for your own profile.'
            }, status=403)
        
        # Trigger the async task
        task = generate_meal_plan.delay(profile_id)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Meal planning process initiated for profile ID: {profile_id}',
            'task_id': task.id
        })
    except Exception as e:
        import logging
        logging.error("Error initiating meal planning process for profile ID %s: %s", profile_id, str(e), exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': 'An internal error occurred while initiating the meal planning process.'
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_email_verification_status(request):
    """
    Check if the current user's email is verified.
    """
    return Response({
        'email_verified': request.user.profile.is_email_verified,
        'email': request.user.email,
        'username': request.user.username
    })
