"""
Meals Services
Business logic for meal-related operations
"""

from sqlalchemy.orm import Session
from models.DbModels.user_health_profile import UserHealthProfile
from models.DbModels.user import User
from models.DbModels.goal import Goal
from models.DbModels.workout_plan import WorkoutPlan
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from schemas.ai_schemas import CreateMealPlanRequest
from ai.services import AIService
import json


async def update_meal_preferences(
    db: Session,
    user_id: int,
    *,
    allergies: Optional[List[str]] = None,
    intolerances: Optional[List[str]] = None,
    diet_type: Optional[str] = None,
    disliked_foods: Optional[List[str]] = None,
    location_country: Optional[str] = None,
    meal_plan_remarks: Optional[str] = None,
) -> UserHealthProfile:
    """
    Update meal preferences for a user in their health profile.
    
    Args:
        db: Database session
        user_id: User ID
        allergies: List of allergies
        intolerances: List of intolerances
        diet_type: Diet type (veg, non_veg, vegan)
        disliked_foods: List of disliked foods
        location_country: Country for ingredient availability
        meal_plan_remarks: Additional remarks
        
    Returns:
        Updated UserHealthProfile object
        
    Raises:
        LookupError: If user health profile does not exist
    """
    # Fetch user health profile
    health_profile = db.query(UserHealthProfile).filter(
        UserHealthProfile.UserId == user_id
    ).first()
    
    if not health_profile:
        raise LookupError(f"Health profile not found for user {user_id}. Please create a health profile first.")
    
    # Update meal-related fields
    if allergies is not None:
        health_profile.Allergies = allergies
    if intolerances is not None:
        health_profile.Intolerances = intolerances
    if diet_type is not None:
        health_profile.DietType = diet_type
    if disliked_foods is not None:
        health_profile.DislikedFoods = disliked_foods
    if location_country is not None:
        health_profile.LocationCountry = location_country
    if meal_plan_remarks is not None:
        health_profile.MealPlanRemarks = meal_plan_remarks
    
    db.commit()
    db.refresh(health_profile)
    
    # Generate meal plan using AI
    try:
        # Fetch user data
        user = db.query(User).filter(User.UserId == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Fetch active goal
        goal = db.query(Goal).filter(
            Goal.UserId == user_id,
            Goal.Active == True
        ).first()
        if not goal:
            raise ValueError(f"No active goal found for user {user_id}. Please set up a fitness goal first.")
        
        # Validate required fields
        if not user.HeightCm or not user.WeightKg:
            raise ValueError(f"User {user_id} is missing required health data (height/weight)")
        
        if not goal.TargetWeight:
            raise ValueError(f"User {user_id} has incomplete goal data. Please complete your fitness goal setup.")
        
        # Map goal type to meal plan goal
        goal_type_map = {
            "weight_loss": "weight_loss",
            "weight_gain": "weight_gain",
            "muscle_gain": "muscle_gain",
            "endurance": "maintenance",
            "strength": "maintenance"
        }
        meal_plan_goal = goal_type_map.get(
            goal.GoalType.value.lower() if goal.GoalType else "maintenance",
            "maintenance"
        )
        
        # Get current day of week
        current_day = datetime.now().strftime("%A")
        
        # Prepare health conditions and medications from health profile
        health_conditions = health_profile.HealthIssues or []
        medications = health_profile.CurrentMedications or []
        
        # Create the AI request
        meal_request = CreateMealPlanRequest(
            user_id=user_id,
            height=int(user.HeightCm),
            weight=float(user.WeightKg),
            target_weight=float(goal.TargetWeight),
            age=user.Age,
            gender=user.Gender.lower() if user.Gender else "male",
            current_day=current_day,
            meal_plan_goal=meal_plan_goal,
            user_remarks=health_profile.MealPlanRemarks,
            allergies=health_profile.Allergies or [],
            intolerances=health_profile.Intolerances or [],
            health_conditions=health_conditions,
            medications=medications,
            diet_type=health_profile.DietType or "non_veg",
            disliked_foods=health_profile.DislikedFoods or [],
            location_country=health_profile.LocationCountry
        )
        
        # Call AI service to generate meal plan
        ai_service = AIService()
        ai_response = await ai_service.generate_meal_plan(meal_request)
        
        # Check if the AI generation was successful
        if not ai_response:
            raise ValueError("AI service failed to generate meal plan")
        
    except Exception as e:
        # Log the error but don't fail the meal preferences update
        # The meal plan can be generated later
        print(f"Warning: Failed to generate meal plan: {str(e)}")
    
    return health_profile


def get_meal_preferences(
    db: Session,
    user_id: int
) -> Optional[UserHealthProfile]:
    """
    Get meal preferences for a user from their health profile.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        UserHealthProfile object or None if not found
    """
    return db.query(UserHealthProfile).filter(
        UserHealthProfile.UserId == user_id
    ).first()


def get_current_meal_plan(
    db: Session,
    user_id: int
) -> Optional[Dict[str, Any]]:
    """
    Get the current meal plan for a user.
    
    Fetches the active workout plan where today's date falls within
    the plan's date range and returns the MealJson.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Dictionary containing the meal plan JSON or None if not found
    """
    today = date.today()
    
    # Find the active workout plan where today's date is within the date range
    workout_plan = (
        db.query(WorkoutPlan)
        .filter(
            WorkoutPlan.UserId == user_id,
            WorkoutPlan.IsActive == True,
            WorkoutPlan.StartDate <= today,
            WorkoutPlan.EndDate >= today
        )
        .first()
    )
    
    if not workout_plan or not workout_plan.MealJson:
        return None
    
    # Parse the MealJson string to dictionary
    try:
        meal_plan = json.loads(workout_plan.MealJson)
        return meal_plan
    except json.JSONDecodeError:
        # If MealJson is not valid JSON, return None
        return None
