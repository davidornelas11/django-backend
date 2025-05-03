import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('GOOGLE_PLACES_API_KEY')
if not api_key:
    print("Error: No API key found in environment variables")
    exit(1)

def test_nearby_places(lat, lng):
    """
    Test the Places API Nearby Search directly with coordinates
    """
    print("\n=== Testing Places API Nearby Search ===")
    
    # Base URL for Places API Nearby Search
    places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    # Required parameters
    params = {
        'location': f"{lat},{lng}",  # latitude,longitude
        'radius': '10000',  # 10km radius (max 50000 meters)
        'type': 'grocery_or_supermarket',  # type of place to search for
        'key': api_key
    }
    
    # Optional parameters
    params.update({
        'keyword': 'supermarket|walmart|frys|aldi|albertsons|safeway',  # keywords to match
        'rankby': 'prominence',  # default ranking
        'language': 'en',  # response language
    })
    
    print(f"Making request to: {places_url}")
    print(f"With params: {params}")
    
    try:
        response = requests.get(places_url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        
        print("\nResponse Status:", data.get('status'))
        
        if data.get('status') == 'OK':
            results = data.get('results', [])
            print(f"\nFound {len(results)} places")
            
            # Print details of each place
            for place in results:
                print("\nStore Details:")
                print(f"Name: {place.get('name')}")
                print(f"Address: {place.get('vicinity')}")
                print(f"Rating: {place.get('rating')}")
                print(f"Types: {', '.join(place.get('types', []))}")
                print(f"Business Status: {place.get('business_status')}")
                
            # Check for additional pages
            if data.get('next_page_token'):
                print("\nMore results available with next_page_token:", data['next_page_token'])
        else:
            print(f"Error: {data.get('status')}")
            if data.get('error_message'):
                print(f"Error message: {data.get('error_message')}")
                
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")

if __name__ == "__main__":
    # Test coordinates for Phoenix, AZ
    phoenix_lat = 33.4484
    phoenix_lng = -112.0740
    
    print(f"Testing with API key: {api_key[:5]}...")
    test_nearby_places(phoenix_lat, phoenix_lng)
