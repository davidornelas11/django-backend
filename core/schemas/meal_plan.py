from typing import List
from langchain_core.pydantic_v1 import BaseModel, Field

class Ingredient(BaseModel):
    name: str
    quantity: float = Field(..., description="numeric quantity, not a string")
    unit: str  # e.g., "g", "kg", "ml", "l", "each"

class Meal(BaseModel):
    name: str
    ingredients: List[Ingredient]
    instructions: List[str]

class DayPlan(BaseModel):
    day: str
    breakfast: Meal
    lunch: Meal
    dinner: Meal

class MealPlan(BaseModel):
    week_of: str  # ISO date like "2025-10-18"
    days: List[DayPlan]
    shopping_list: List[Ingredient]
    total_estimated_cost: float
    cart_instructions: List[str]