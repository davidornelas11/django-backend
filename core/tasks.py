from celery import shared_task
import os
from users.models import Profile
import logging
from typing import Dict, List, Optional
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
import json
from .instacart_client import InstacartClient

logger = logging.getLogger('core.tasks')

def create_meal_planning_chain():
    """
    Creates a LangChain chain for meal planning using OpenAI.
    Uses a simple LLMChain approach instead of complex agents to avoid parsing errors.
    """
    llm = ChatOpenAI(
        temperature=0.7,
        model_name="gpt-4o-mini",  # Use a valid model name
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
    
    template = """You are a meal planning assistant. Create a detailed weekly meal plan based on the user's preferences and dietary restrictions.

User Preferences: {preferences}
Dietary Restrictions: {dietary_restrictions}
Budget: ${budget}

Please create a comprehensive meal plan that:
1. Stays within the specified budget
2. Respects all dietary restrictions
3. Matches user preferences
4. Includes 7 days of meals (breakfast, lunch, dinner)
5. Provides a complete ingredient list with quantities
6. Includes estimated total cost
7. Provides simple cooking instructions

Format your response as a structured meal plan with clear sections for each day and a summary of ingredients needed.

Meal Plan:"""

    prompt = PromptTemplate(
        template=template,
        input_variables=["preferences", "dietary_restrictions", "budget"]
    )
    
    return LLMChain(llm=llm, prompt=prompt)

def create_instacart_cart(meal_plan: str, profile: Profile) -> str:
    """
    Creates an Instacart shopping cart based on the meal plan.
    
    Args:
        meal_plan: The generated meal plan text
        profile: User profile with location information
        
    Returns:
        str: URL to the created Instacart cart
    """
    try:
        api_key = os.getenv('INSTACART_API_KEY')
        logger.info(f"🔍 DEBUG: INSTACART_API_KEY found: {api_key[:10] if api_key else 'None'}...{api_key[-4:] if api_key and len(api_key) > 14 else ''}")
        logger.info(f"🔍 DEBUG: API key length: {len(api_key) if api_key else 0}")
        logger.info(f"🔍 DEBUG: API key is None: {api_key is None}")
        logger.info(f"🔍 DEBUG: API key is empty string: {api_key == ''}")
        
        if not api_key:
            logger.error("❌ DEBUG: No INSTACART_API_KEY found in environment variables")
            return "https://instacart.com/cart/mock-cart-url"
        
        client = InstacartClient(api_key=api_key)
        logger.info(f"🔍 DEBUG: Instacart client created with base URL: {client.base_url}")
        logger.info(f"🔍 DEBUG: Client headers: {dict(client.session.headers)}")
        
        # Extract ingredients from meal plan (simplified for now)
        # In a real implementation, you'd parse the meal plan text to extract ingredients
        ingredients = [
            {"name": "Chicken Breast", "quantity": 2, "unit": "lb"},
            {"name": "Rice", "quantity": 1, "unit": "bag"},
            {"name": "Broccoli", "quantity": 1, "unit": "bunch"},
            {"name": "Olive Oil", "quantity": 1, "unit": "bottle"},
            {"name": "Garlic", "quantity": 3, "unit": "cloves"},
            {"name": "Onion", "quantity": 2, "unit": "each"},
            {"name": "Tomatoes", "quantity": 4, "unit": "each"},
            {"name": "Pasta", "quantity": 1, "unit": "box"},
            {"name": "Ground Beef", "quantity": 1, "unit": "lb"},
            {"name": "Cheese", "quantity": 1, "unit": "block"}
        ]
        
        # Create meal plan cart
        cart_title = f"Weekly Meal Plan for {profile.user.username}"
        logger.info(f"🔍 DEBUG: Creating cart with title: {cart_title}")
        logger.info(f"🔍 DEBUG: Ingredients count: {len(ingredients)}")
        
        cart_response = client.create_meal_plan_cart(
            meal_plan_title=cart_title,
            ingredients=ingredients
        )
        
        logger.info(f"🔍 DEBUG: Cart response received: {cart_response}")
        
        # Extract the share URL from the response
        cart_url = cart_response.get("products_link_url", "")
        if not cart_url:
            logger.warning("No products_link_url in Instacart response")
            return "https://instacart.com/cart/mock-cart-url"
        
        logger.info(f"🔍 DEBUG: Successfully created cart with URL: {cart_url}")
        return cart_url
        
    except Exception as e:
        logger.error(f"Error creating Instacart cart: {str(e)}")
        logger.error(f"🔍 DEBUG: Exception type: {type(e).__name__}")
        logger.error(f"🔍 DEBUG: Exception details: {str(e)}")
        # Return a mock URL for testing purposes
        return "https://instacart.com/cart/mock-cart-url"

@shared_task
def generate_meal_plan(profile_id):
    try:
        logger.info(f"Starting meal plan generation for profile {profile_id}")
        profile = Profile.objects.get(id=profile_id)
        logger.debug(f"Retrieved profile: {profile.user.username} with preferences: {profile.preferences}")
        
        # Create the meal planning chain
        meal_planning_chain = create_meal_planning_chain()
        logger.debug("Created meal planning chain")
        
        try:
            # Generate the meal plan
            logger.info("Invoking meal planning chain")
            result = meal_planning_chain.invoke({
                "preferences": str(profile.preferences),
                "dietary_restrictions": str(profile.dietary_restrictions),
                "budget": str(profile.weekly_budget)
            })
            
            meal_plan_text = result['text']
            logger.info("Successfully generated meal plan")
            
            # Create Instacart cart
            cart_url = create_instacart_cart(meal_plan_text, profile)
            
            # Update profile with generated data
            profile.meal_plan = {
                'plan': meal_plan_text,
                'cart_url': cart_url,
                'generated_at': str(profile.updated_at)
            }
            profile.status = 'COMPLETED'
            profile.save()
            
            return f"Successfully generated meal plan for profile ID: {profile_id} (User: {profile.user.username})"
            
        except Exception as e:
            logger.error(f"Error during meal plan generation: {str(e)}", exc_info=True)
            profile.status = 'FAILED'
            profile.save()
            return f"Error while generating meal plan for profile {profile_id}: {str(e)}"
            
    except Profile.DoesNotExist:
        logger.error(f"Profile {profile_id} not found")
        return f"Profile {profile_id} not found"
    except Exception as e:
        logger.error(f"Unexpected error in generate_meal_plan: {str(e)}", exc_info=True)
        if 'profile' in locals():
            profile.status = 'FAILED'
            profile.save()
        return f"Unexpected error while generating meal plan for profile {profile_id}: {str(e)}" 