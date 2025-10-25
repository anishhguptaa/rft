"""
Meals Routes
Handles endpoints for meal preferences
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db import get_db
from api.modules.meals.services import update_meal_preferences, get_meal_preferences, get_current_meal_plan
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter()


# Request schemas
class UpdateMealPreferencesRequest(BaseModel):
    allergies: Optional[List[str]] = Field(
        None, description="List of allergies (e.g., peanut, shellfish)"
    )
    intolerances: Optional[List[str]] = Field(
        None, description="List of intolerances (e.g., lactose, gluten)"
    )
    diet_type: Optional[str] = Field(
        None, description="Diet type: veg, non_veg, vegan"
    )
    disliked_foods: Optional[List[str]] = Field(
        None, description="List of disliked foods"
    )
    location_country: Optional[str] = Field(
        None, description="Country for ingredient availability and cuisine suggestions"
    )
    meal_plan_remarks: Optional[str] = Field(
        None, description="Additional remarks about meal preferences"
    )


# Response schemas
class MealPreferencesResponse(BaseModel):
    user_id: int
    allergies: Optional[List[str]] = None
    intolerances: Optional[List[str]] = None
    diet_type: Optional[str] = None
    disliked_foods: Optional[List[str]] = None
    location_country: Optional[str] = None
    meal_plan_remarks: Optional[str] = None


@router.put("/users/{user_id}/meal-preferences", response_model=MealPreferencesResponse)
async def update_user_meal_preferences(
    user_id: int,
    payload: UpdateMealPreferencesRequest,
    db: Session = Depends(get_db),
):
    """
    Update meal preferences for a user.
    
    Updates the meal-related fields in the user's health profile.
    The user must have an existing health profile.
    
    Automatically generates a meal plan using AI after preferences are updated.
    
    Args:
        user_id: User ID
        payload: Meal preferences data
        
    Returns:
        Updated meal preferences
        
    Raises:
        404: If user health profile not found
    """
    try:
        health_profile = await update_meal_preferences(
            db,
            user_id,
            allergies=payload.allergies,
            intolerances=payload.intolerances,
            diet_type=payload.diet_type,
            disliked_foods=payload.disliked_foods,
            location_country=payload.location_country,
            meal_plan_remarks=payload.meal_plan_remarks,
        )
        
        return MealPreferencesResponse(
            user_id=health_profile.UserId,
            allergies=health_profile.Allergies,
            intolerances=health_profile.Intolerances,
            diet_type=health_profile.DietType,
            disliked_foods=health_profile.DislikedFoods,
            location_country=health_profile.LocationCountry,
            meal_plan_remarks=health_profile.MealPlanRemarks,
        )
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating meal preferences: {str(e)}")


@router.get("/users/{user_id}/meal-preferences", response_model=MealPreferencesResponse)
def get_user_meal_preferences(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Get meal preferences for a user.
    
    Retrieves the meal-related fields from the user's health profile.
    
    Args:
        user_id: User ID
        
    Returns:
        User's meal preferences
        
    Raises:
        404: If user health profile not found
    """
    health_profile = get_meal_preferences(db, user_id)
    
    if not health_profile:
        raise HTTPException(
            status_code=404,
            detail=f"Health profile not found for user {user_id}"
        )
    
    return MealPreferencesResponse(
        user_id=health_profile.UserId,
        allergies=health_profile.Allergies,
        intolerances=health_profile.Intolerances,
        diet_type=health_profile.DietType,
        disliked_foods=health_profile.DislikedFoods,
        location_country=health_profile.LocationCountry,
        meal_plan_remarks=health_profile.MealPlanRemarks,
    )


@router.get("/users/{user_id}/meal-plan")
def get_user_meal_plan(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Get the current meal plan for a user.
    
    Retrieves the meal plan from the active workout plan where today's date
    falls within the plan's date range (StartDate to EndDate).
    
    Args:
        user_id: User ID
        
    Returns:
        Meal plan JSON object
        
    Raises:
        404: If no active meal plan found
    """
    meal_plan = get_current_meal_plan(db, user_id)
    
    if not meal_plan:
        raise HTTPException(
            status_code=404,
            detail=f"No active meal plan found for user {user_id}. Please update your meal preferences to generate a meal plan."
        )
    
    return meal_plan
