from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from core.tasks import run_scraper_task

# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_scrape_view(request, profile_id):
    """
    Trigger the scraping process for a specific profile.
    
    Args:
        request: The HTTP request object
        profile_id: The ID of the profile to scrape
    """
    try:
        # Trigger the async task
        task = run_scraper_task.delay(profile_id)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Scraping process initiated for profile ID: {profile_id}',
            'task_id': task.id
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to initiate scraping process: {str(e)}'
        }, status=500)
