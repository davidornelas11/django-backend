import requests
import json
import os
from typing import Dict, List, Optional
import logging

class InstacartClient:
    """
    A client for interacting with the Instacart API.
    Uses the correct endpoints and request format from the official API.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://connect.dev.instacart.tools"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
    
    def create_shopping_cart(self, title: str, line_items: List[Dict], instructions: List[str] = None) -> Dict:
        """
        Creates a shopping cart using the Instacart Products Link API.
        
        Args:
            title: Title for the shopping cart
            line_items: List of items to add to the cart
            instructions: Optional list of instructions for the cart
            
        Returns:
            Dict: Response from the API containing the cart information
        """
        url = f"{self.base_url}/idp/v1/products/products_link"
        
        payload = {
            "title": title,
            "image_url": "",  # Optional: can be empty string
            "link_type": "shopping_list",
            "expires_in": 7,  # In days, not seconds
            "instructions": instructions or [],
            "line_items": line_items,
            "landing_page_configuration": {
                "partner_linkback_url": "",
                "enable_pantry_items": True
            }
        }
        
        # Debug logging
        logger = logging.getLogger('core.tasks')
        logger.info(f"🔍 DEBUG: Making request to URL: {url}")
        logger.info(f"🔍 DEBUG: Request headers: {dict(self.session.headers)}")
        logger.info(f"🔍 DEBUG: Request payload: {json.dumps(payload, indent=2)}")
        logger.info(f"🔍 DEBUG: Authorization header: Bearer {self.api_key[:10]}...{self.api_key[-4:] if len(self.api_key) > 14 else ''}")
        
        response = self.session.post(url, json=payload)
        
        logger.info(f"🔍 DEBUG: Response status code: {response.status_code}")
        logger.info(f"🔍 DEBUG: Response headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            logger.info(f"🔍 DEBUG: Response body: {json.dumps(response_json, indent=2)}")
        except Exception as e:
            logger.info(f"🔍 DEBUG: Could not parse response as JSON: {response.text}")
        
        response.raise_for_status()
        return response.json()
    
    def create_meal_plan_cart(self, meal_plan_title: str, ingredients: List[Dict]) -> Dict:
        """
        Creates a shopping cart specifically for meal plan ingredients.
        
        Args:
            meal_plan_title: Title for the meal plan
            ingredients: List of ingredients with name, quantity, and unit
            
        Returns:
            Dict: Response from the API containing the cart information
        """
        # Convert ingredients to the format expected by Instacart API
        line_items = []
        for ingredient in ingredients:
            line_item = {
                "name": ingredient.get("name", ""),
                "quantity": ingredient.get("quantity", 1),
                "unit": ingredient.get("unit", "each"),
                "display_text": f"{ingredient.get('quantity', 1)} {ingredient.get('unit', 'each')} {ingredient.get('name', '')}",
                "line_item_measurements": [
                    {
                        "quantity": ingredient.get("quantity", 1),
                        "unit": ingredient.get("unit", "each")
                    }
                ],
                "filters": {
                    "brand_filters": [],
                    "health_filters": []
                }
            }
            line_items.append(line_item)
        
        instructions = [
            "This shopping list was generated from your meal plan",
            "Please review quantities and brands before purchasing"
        ]
        
        return self.create_shopping_cart(
            title=meal_plan_title,
            line_items=line_items,
            instructions=instructions
        )

class Cart:
    """
    Represents a shopping cart in the Instacart system.
    Note: This is now a simplified wrapper around the API response.
    """
    
    def __init__(self, client: InstacartClient, cart_data: Dict):
        self.client = client
        self.cart_data = cart_data
        self.cart_id = cart_data.get("id", "")
        self.share_url = cart_data.get("share_url", "")
    
    def get_share_url(self) -> str:
        """
        Gets the shareable URL for the cart.
        
        Returns:
            str: URL to share the cart
        """
        return self.share_url
    
    def get_cart_data(self) -> Dict:
        """
        Gets the complete cart data.
        
        Returns:
            Dict: Complete cart information
        """
        return self.cart_data 