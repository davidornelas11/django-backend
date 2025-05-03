from celery import shared_task
import requests
import time
import os
from users.models import Profile
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

def get_nearby_grocery_stores(lat: float, lng: float, api_key: str) -> List[Dict]:
    """
    Get nearby large grocery stores using Google Places API.
    
    Args:
        lat: Latitude of the location
        lng: Longitude of the location
        api_key: Google Places API key
        
    Returns:
        List of dictionaries containing store information
    """
    target_stores = ['frys', 'aldi', 'walmart', 'albertsons', 'safeway']
    
    try:
        logger.info(f"Searching for stores near: lat={lat}, lng={lng}")
        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        places_params = {
            'location': f"{lat},{lng}",
            'radius': '10000',  # 10km radius (max 50000 meters)
            'type': 'grocery_or_supermarket',
            'keyword': 'supermarket|walmart|frys|aldi|albertsons|safeway',
            'rankby': 'prominence',
            'language': 'en',
            'key': api_key
        }
        logger.info(f"Making places API request to: {places_url}")
        logger.info(f"ENTIRE URL WITH PARAMS: {places_url}?{places_params}")
        places_response = requests.get(places_url, params=places_params)
        places_response.raise_for_status()
        places_data = places_response.json()
        
        if places_data.get('status') != 'OK':
            logger.error(f"Places API error - Status: {places_data.get('status')}, Error Message: {places_data.get('error_message', 'No error message')}")
            return []
        
        filtered_stores = []
        results = places_data.get('results', [])
        logger.info(f"Found {len(results)} total places before filtering")
        
        for place in results:
            name = place.get('name', '').lower()
            if any(store in name for store in target_stores):
                store_info = {
                    'name': place.get('name'),
                    'address': place.get('vicinity'),
                    'rating': place.get('rating'),
                    'place_id': place.get('place_id'),
                    'business_status': place.get('business_status'),
                    'types': place.get('types', []),
                    'location': {
                        'lat': place.get('geometry', {}).get('location', {}).get('lat'),
                        'lng': place.get('geometry', {}).get('location', {}).get('lng')
                    }
                }
                filtered_stores.append(store_info)
                logger.info(f"Found matching store: {store_info['name']} at {store_info['address']}")
        
        if places_data.get('next_page_token'):
            logger.info("More results available with next_page_token")
        
        logger.info(f"Found {len(filtered_stores)} matching stores near lat={lat}, lng={lng}")
        return filtered_stores
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching nearby stores for lat={lat}, lng={lng}: {str(e)}")
        logger.error(f"Request error details: {str(e.__dict__)}")
        return []

@shared_task
def run_scraper_task(profile_id: int):
    """
    A Celery task that runs a scraper for a specific profile.
    
    Args:
        profile_id (int): The ID of the profile to scrape data for
    """
    try:
        # Get the profile
        profile = Profile.objects.get(id=profile_id)
        
        # Update status to PROCESSING
        profile.status = 'PROCESSING'
        profile.save()
        
        # Get API keys from environment variables
        google_api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        scraper_api_url = os.getenv('SCRAPER_API_URL')
        
        if not all([google_api_key, scraper_api_url]):
            raise ValueError("Missing required API keys in environment variables")
        
        # Get nearby grocery stores if coordinates are available
        nearby_stores = []
        if profile.latitude is not None and profile.longitude is not None:
            nearby_stores = get_nearby_grocery_stores(profile.latitude, profile.longitude, google_api_key)
        else:
            logger.warning(f"No latitude/longitude found for profile {profile_id}")
        
        # Make the POST request to the scraper API
        response = requests.post(
            scraper_api_url,
            json={
                'profile_id': profile_id,
                'nearby_stores': nearby_stores
            },
            timeout=180  # 3 minutes timeout
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # Update profile with scraped data
        profile.scraped_data = {
            'api_data': data,
            'nearby_stores': nearby_stores
        }
        profile.status = 'COMPLETED'
        profile.save()
        
        return f"Successfully scraped data for profile ID: {profile_id} (User: {profile.user.username})"
        
    except Profile.DoesNotExist:
        logger.error(f"Profile with ID {profile_id} does not exist")
        return f"Profile with ID {profile_id} does not exist"
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while scraping profile {profile_id}: {str(e)}")
        if 'profile' in locals():
            profile.status = 'FAILED'
            profile.save()
        return f"Network error while scraping profile {profile_id}: {str(e)}"
        
    except Exception as e:
        logger.error(f"Unexpected error while scraping profile {profile_id}: {str(e)}")
        if 'profile' in locals():
            profile.status = 'FAILED'
            profile.save()
        return f"Unexpected error while scraping profile {profile_id}: {str(e)}" 