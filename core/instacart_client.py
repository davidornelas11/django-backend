import requests
import json
import os
from typing import Dict, List, Optional

class InstacartClient:
    """
    A client for interacting with the Instacart API.
    """
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.instacart.com/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def create_cart(self, store_id: str, delivery_address: Dict[str, float]) -> 'Cart':
        """
        Creates a new shopping cart for a specific store.
        
        Args:
            store_id: The ID of the store to create the cart for
            delivery_address: Dictionary containing latitude and longitude
            
        Returns:
            Cart: A Cart object for managing items
        """
        response = self.session.post(
            f"{self.base_url}/carts",
            json={
                "store_id": store_id,
                "delivery_address": delivery_address
            }
        )
        response.raise_for_status()
        cart_data = response.json()
        return Cart(self, cart_data["cart_id"])
    
    def get_store_info(self, store_id: str) -> Dict:
        """
        Gets information about a specific store.
        
        Args:
            store_id: The ID of the store
            
        Returns:
            Dict: Store information
        """
        response = self.session.get(f"{self.base_url}/stores/{store_id}")
        response.raise_for_status()
        return response.json()

class Cart:
    """
    Represents a shopping cart in the Instacart system.
    """
    
    def __init__(self, client: InstacartClient, cart_id: str):
        self.client = client
        self.cart_id = cart_id
        self.items = []
    
    def add_item(self, name: str, quantity: float, unit: str) -> None:
        """
        Adds an item to the cart.
        
        Args:
            name: Name of the item
            quantity: Quantity to add
            unit: Unit of measurement (e.g., "oz", "lb", "each")
        """
        self.items.append({
            "name": name,
            "quantity": quantity,
            "unit": unit
        })
    
    def get_share_url(self) -> str:
        """
        Gets a shareable URL for the cart.
        
        Returns:
            str: URL to share the cart
        """
        response = self.client.session.post(
            f"{self.client.base_url}/carts/{self.cart_id}/share"
        )
        response.raise_for_status()
        return response.json()["share_url"] 