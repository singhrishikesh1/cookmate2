from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from models import UserPersona 
from pydantic import BaseModel
from typing import List

class RecipeStep(BaseModel):
    step_number: int
    instruction: str
    duration_seconds: int

class Recipe(BaseModel):
    dish_name: str
    description: str
    effort_score: int
    protein_content: str
    steps: List[str]
class RecipeList(BaseModel):
    recipes: List[Recipe]

class RecipeRequest(BaseModel):
    user_id: int
    meal_type: str

# --- 1. INVENTORY ---
class InventoryItemBase(BaseModel):
    name: str
    quantity: float
    unit: str
    expiry_date: Optional[datetime] = None

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItem(InventoryItemBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    username: str
    preferences: str = "None"
    dietary_goal: str = "Balanced"
    allergies: str = "None"
    persona: UserPersona = UserPersona.HOSTELER
    current_effort_level: str = "normal"
    planning_horizon: str = "daily"

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    portion_multiplier: float = 1.0
    streak_count: int = 0
    model_config = ConfigDict(from_attributes=True)

class CookingStep(BaseModel):
    step_number: int
    instruction: str
    duration_seconds: int = Field(default=60, alias="duration") 
    heat_level: str = "medium"
    visual_cue: Optional[str] = "Look for a change in color."

    @field_validator('duration_seconds', mode='before')
    @classmethod
    def validate_int(cls, v):
        if isinstance(v, str):
            return int(v.split()[0]) 
        return v

class StructuredRecipe(BaseModel):
    dish_name: str
    description: str = "A delicious AI-curated meal."
    ingredients: List[str] = []
    equipment: List[str] = []
    steps: List[CookingStep]
    total_time_minutes: int = 15
    macros_estimate: Dict[str, str] = {"calories": "unknown", "protein": "unknown"}
    effort_score: float = 5.0
    prep_time_minutes: int = 5
    cleanup_score: str = "medium"

class SessionStartRequest(BaseModel):
    user_id: int
    recipe_data: StructuredRecipe 

class MentorStepResponse(BaseModel):
    session_id: int
    step_number: int
    total_steps: int
    instruction: str
    timer_seconds: int
    visual_cue: Optional[str] = None
    voice_response_text: str 
    all_step_timers: List[int] = []

class DayPlanRequest(BaseModel):
    user_id: int
    diet_preference: str = "non-veg"