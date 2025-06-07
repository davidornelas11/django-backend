from celery import shared_task
import os
from users.models import Profile
import logging
from typing import Dict, List, Optional
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.tools import DuckDuckGoSearchRun
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.agents.output_parsers import ReActSingleInputOutputParser
import json
from .instacart_client import InstacartClient

logger = logging.getLogger('core.tasks')

def create_meal_planning_chain():
    """
    Creates a LangChain chain for meal planning using OpenAI.
    """
    llm = ChatOpenAI(
        temperature=0.7,
        model_name="gpt-4.1-nano",
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
    
    search = DuckDuckGoSearchRun()
    
    tools = [
        Tool(
            name="Search",
            func=search.run,
            description="Useful for searching current prices and availability of ingredients"
        )
    ]
    
    template = """You are a meal planning assistant. Your task is to create a weekly meal plan based on the user's preferences and dietary restrictions.
    
    User Preferences: {preferences}
    Dietary Restrictions: {dietary_restrictions}
    Budget: {budget}
    
    Use the Search tool to find current prices of ingredients and create a meal plan that:
    1. Stays within budget
    2. Respects dietary restrictions
    3. Matches user preferences
    4. Uses ingredients that are currently available and affordable
    
    Create a detailed meal plan with:
    - 7 days of meals (breakfast, lunch, dinner)
    - Complete ingredient list with quantities
    - Estimated total cost
    - Instructions for each recipe
    
    {agent_scratchpad}"""
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["preferences", "dietary_restrictions", "budget", "agent_scratchpad"]
    )
    
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    
    output_parser = ReActSingleInputOutputParser()
    
    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        allowed_tools=[tool.name for tool in tools],
        stop=["\nObservation:"],
        handle_parsing_errors=True,
        output_parser=output_parser
    )
    
    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=ConversationBufferMemory(memory_key="chat_history")
    )

def create_instacart_cart(meal_plan: Dict, profile: Profile) -> str:
    """
    Creates an Instacart shopping cart based on the meal plan.
    
    Args:
        meal_plan: The generated meal plan
        profile: User profile with location information
        
    Returns:
        str: URL to the created Instacart cart
    """
    client = InstacartClient(
        api_key=os.getenv('INSTACART_API_KEY'),
        api_secret=os.getenv('INSTACART_API_SECRET')
    )
    
    # Create a new cart
    cart = client.create_cart(
        store_id=profile.preferred_store_id,
        delivery_address={
            'latitude': profile.latitude,
            'longitude': profile.longitude
        }
    )
    
    # Add items to cart
    for ingredient in meal_plan['ingredients']:
        cart.add_item(
            name=ingredient['name'],
            quantity=ingredient['quantity'],
            unit=ingredient['unit']
        )
    
    # Get cart URL
    cart_url = cart.get_share_url()
    return cart_url

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
            meal_plan = meal_planning_chain.invoke({
                "preferences": profile.preferences,
                "dietary_restrictions": profile.dietary_restrictions,
                "budget": profile.weekly_budget,
                "agent_scratchpad": ""  # Initialize with empty scratchpad
            })
            logger.info("Successfully generated meal plan")
            
            # Create Instacart cart
            cart_url = create_instacart_cart(meal_plan, profile)
            
            # Update profile with generated data
            profile.meal_plan = {
                'plan': meal_plan,
                'cart_url': cart_url
            }
            profile.status = 'COMPLETED'
            profile.save()
            
            return f"Successfully generated meal plan for profile ID: {profile_id} (User: {profile.user.username})"
        except Exception as e:
            logger.error(f"Error during meal plan generation: {str(e)}", exc_info=True)
            return f"Unexpected error while generating meal plan for profile {profile_id}: {str(e)}"
            
    except Profile.DoesNotExist:
        logger.error(f"Profile {profile_id} not found")
        return f"Profile {profile_id} not found"
    except Exception as e:
        logger.error(f"Unexpected error in generate_meal_plan: {str(e)}", exc_info=True)
        if 'profile' in locals():
            profile.status = 'FAILED'
            profile.save()
        return f"Unexpected error while generating meal plan for profile {profile_id}: {str(e)}" 