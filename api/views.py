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
def get_meal_plan(request):
    """
    Retrieve the current user's meal plan.
    Returns the meal plan data if it exists, otherwise returns a message indicating no meal plan exists.
    """
    try:
        profile = request.user.profile
        
        if not profile.meal_plan:
            return Response({
                'status': 'no_meal_plan',
                'message': 'No meal plan found. Create one first using the meal plan generation endpoint.',
                'meal_plan': None
            }, status=200)
        
        return Response({
            'status': 'success',
            'message': 'Meal plan retrieved successfully',
            'meal_plan': profile.meal_plan,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email
            },
            'profile_info': {
                'weekly_budget': profile.weekly_budget,
                'dietary_restrictions': profile.dietary_restrictions,
                'preferences': profile.preferences,
                'location': profile.location
            }
        })
        
    except Exception as e:
        import logging
        logging.error("Error retrieving meal plan for user %s: %s", request.user.username, str(e), exc_info=True)
        return Response({
            'status': 'error',
            'message': 'An error occurred while retrieving the meal plan.'
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_meal_plan_history(request):
    """
    Retrieve the current user's meal plan history.
    Supports pagination and filtering by date range.
    """
    try:
        from users.models import MealPlanHistory
        from datetime import datetime, date
        
        # Get query parameters
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        year = request.GET.get('year')
        month = request.GET.get('month')
        
        # Base queryset
        queryset = MealPlanHistory.objects.filter(user=request.user)
        
        # Apply filters
        if year:
            queryset = queryset.filter(year=int(year))
        if month:
            queryset = queryset.filter(month=int(month))
        
        # Get total count
        total_count = queryset.count()
        
        # Apply pagination
        history_entries = queryset[offset:offset + limit]
        
        # Serialize the data
        history_data = []
        for entry in history_entries:
            history_data.append({
                'id': entry.id,
                'week_start_date': entry.week_start_date.isoformat(),
                'week_end_date': entry.week_end_date.isoformat(),
                'year': entry.year,
                'month': entry.month,
                'week_number': entry.week_number,
                'total_budget': float(entry.total_budget) if entry.total_budget else None,
                'meal_count': entry.get_meal_count(),
                'shopping_list_items': entry.get_shopping_list_items(),
                'was_completed': entry.was_completed,
                'user_rating': entry.user_rating,
                'notes': entry.notes,
                'created_at': entry.created_at.isoformat(),
                'archived_at': entry.archived_at.isoformat(),
            })
        
        return Response({
            'status': 'success',
            'message': 'Meal plan history retrieved successfully',
            'data': {
                'history': history_data,
                'pagination': {
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total_count
                }
            }
        })
        
    except Exception as e:
        import logging
        logging.error(f"Error retrieving meal plan history for user {request.user.username}: {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': 'An error occurred while retrieving meal plan history.'
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_meal_plan_history_detail(request, history_id):
    """
    Retrieve detailed information about a specific historical meal plan.
    """
    try:
        from users.models import MealPlanHistory
        
        # Get the specific history entry
        history_entry = MealPlanHistory.objects.get(
            id=history_id,
            user=request.user  # Ensure user can only access their own history
        )
        
        return Response({
            'status': 'success',
            'message': 'Historical meal plan retrieved successfully',
            'data': {
                'id': history_entry.id,
                'week_start_date': history_entry.week_start_date.isoformat(),
                'week_end_date': history_entry.week_end_date.isoformat(),
                'year': history_entry.year,
                'month': history_entry.month,
                'week_number': history_entry.week_number,
                'total_budget': float(history_entry.total_budget) if history_entry.total_budget else None,
                'meal_plan_data': history_entry.meal_plan_data,
                'was_completed': history_entry.was_completed,
                'user_rating': history_entry.user_rating,
                'notes': history_entry.notes,
                'created_at': history_entry.created_at.isoformat(),
                'archived_at': history_entry.archived_at.isoformat(),
            }
        })
        
    except MealPlanHistory.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Historical meal plan not found or access denied.'
        }, status=404)
    except Exception as e:
        import logging
        logging.error(f"Error retrieving historical meal plan {history_id} for user {request.user.username}: {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': 'An error occurred while retrieving the historical meal plan.'
        }, status=500)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_meal_plan_history(request, history_id):
    """
    Update a historical meal plan (rating, completion status, notes).
    """
    try:
        from users.models import MealPlanHistory
        
        # Get the specific history entry
        history_entry = MealPlanHistory.objects.get(
            id=history_id,
            user=request.user
        )
        
        # Update allowed fields
        if 'was_completed' in request.data:
            history_entry.was_completed = request.data['was_completed']
        
        if 'user_rating' in request.data:
            rating = request.data['user_rating']
            if rating is not None and (rating < 1 or rating > 5):
                return Response({
                    'status': 'error',
                    'message': 'Rating must be between 1 and 5.'
                }, status=400)
            history_entry.user_rating = rating
        
        if 'notes' in request.data:
            history_entry.notes = request.data['notes']
        
        history_entry.save()
        
        return Response({
            'status': 'success',
            'message': 'Historical meal plan updated successfully',
            'data': {
                'id': history_entry.id,
                'was_completed': history_entry.was_completed,
                'user_rating': history_entry.user_rating,
                'notes': history_entry.notes,
            }
        })
        
    except MealPlanHistory.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Historical meal plan not found or access denied.'
        }, status=404)
    except Exception as e:
        import logging
        logging.error(f"Error updating historical meal plan {history_id} for user {request.user.username}: {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': 'An error occurred while updating the historical meal plan.'
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def archive_current_meal_plan(request):
    """
    Manually archive the current meal plan without generating a new one.
    """
    try:
        profile = request.user.profile
        
        if not profile.meal_plan:
            return Response({
                'status': 'no_meal_plan',
                'message': 'No current meal plan to archive.'
            }, status=200)
        
        # Archive the current meal plan
        archived = profile.archive_current_meal_plan()
        
        if archived:
            return Response({
                'status': 'success',
                'message': 'Current meal plan archived successfully',
                'data': {
                    'archived_id': archived.id,
                    'week_start_date': archived.week_start_date.isoformat(),
                    'week_end_date': archived.week_end_date.isoformat(),
                }
            })
        else:
            return Response({
                'status': 'error',
                'message': 'Failed to archive current meal plan.'
            }, status=500)
            
    except Exception as e:
        import logging
        logging.error(f"Error archiving current meal plan for user {request.user.username}: {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': 'An error occurred while archiving the meal plan.'
        }, status=500)
