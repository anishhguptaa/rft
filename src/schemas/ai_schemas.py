"""
AI Schemas
Pydantic models for AI endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal


# Helper Schemas

Gender = Literal["male", "female"]
DietType = Literal["veg", "non_veg", "vegan"]
WorkoutGoal = Literal[
    "weight_loss", "weight_gain", "muscle_gain", "endurance", "strength"
]
MealPlanGoal = Literal["weight_loss", "weight_gain", "muscle_gain", "maintenance"]
ExperienceLevel = Literal["beginner", "intermediate", "advanced"]


class Exercise(BaseModel):
    """Individual exercise model with comprehensive details for workout execution"""

    name: str = Field(
        ...,
        description="Specific name of the exercise (e.g., 'Barbell Back Squat', 'Push-ups')",
    )
    sets: int = Field(..., description="Number of sets to perform")
    reps: List[int] = Field(..., description="List of number of reps for each set")
    weights_used: List[float] = Field(
        ..., description="List of weights used for each set in kilograms"
    )


class MealPlan(BaseModel):
    """Model for a meal plan with comprehensive details for meal execution"""

    name: str = Field(
        ...,
        description="Unique name of the meal.",
    )
    time_of_day: str = Field(..., description="When the meal is to be eaten. e.g., 'Breakfast', 'Lunch', 'Dinner', 'Snack', 'Pre-Workout Meal', 'Post-Workout Meal'")
    description: str = Field(..., description="What to actually eat in the meal")
    ingredients: List[str] = Field(..., description="Key ingredients for the meal, maximum 3-5 ingredients")


class DailyMealPlan(BaseModel):
    """Model for a daily meal plan with comprehensive details for meal execution"""

    day_of_week: str = Field(..., description="Day of the week")
    meals: List[MealPlan] = Field(..., description="List of meals for the day")


class Routine(BaseModel):
    """Model for a routine with comprehensive details for workout execution"""

    name: str = Field(
        ...,
        description="Unique name of the routine. If there are 2 push days or 2 upper body days, the name should be 'Push Day 1'/ 'Push Day 2' or 'Upper Body Day 1'/ 'Upper Body Day 2'",
    )
    focus: str = Field(..., description="Primary focus of the routine")
    exercises: List[Exercise] = Field(
        ..., description="List of exercises for this routine"
    )


class DailySchedule(BaseModel):
    """Model for a daily schedule with comprehensive details for workout execution"""

    day_of_week: str = Field(..., description="Day of the week")
    routine_name: str = Field(
        ..., description="Name of the routine from the routines list for this day"
    )


# Request Schemas
class CreateFirstWorkoutRequest(BaseModel):
    user_id: int = Field(..., description="User token")
    height: int = Field(..., description="Height in centimeters")
    weight: float = Field(..., description="Weight in kilograms")
    target_weight: float = Field(..., description="Target weight in kilograms")
    age: int = Field(..., description="Age in years")
    gender: Gender = Field(..., description="Gender")
    workout_goal: WorkoutGoal = Field(
        ...,
        description="Primary workout goal",
    )
    goal_timeline: int = Field(..., description="Target goal timeline in weeks")
    workout_days: int = Field(..., description="Number of days to workout in the week")
    current_day: str = Field(..., description="Current day of the week")
    equipment: str = Field(
        ...,
        description="Available equipment (e.g., gym, home_bodyweight, home_dumbbells)",
    )
    experience_level: ExperienceLevel = Field(
        ..., description="Fitness experience level"
    )
    user_limitations: Optional[List[str]] = Field(
        None,
        description="List of user limitations (e.g., injuries, medical conditions, mobility restrictions)",
    )
    user_remarks: Optional[str] = Field(
        None, description="Additional user remarks about the workout plan"
    )


class ContinueWorkoutRequest(BaseModel):
    user_id: int = Field(..., description="User token")
    height: int = Field(..., description="Height in centimeters")
    weight: float = Field(..., description="Weight in kilograms")
    target_weight: float = Field(..., description="Target weight in kilograms")
    age: int = Field(..., description="Age in years")
    gender: Gender = Field(..., description="Gender")
    workout_goal: WorkoutGoal = Field(
        ...,
        description="Primary workout goal",
    )
    goal_timeline: int = Field(..., description="Target goal timeline in weeks")
    workout_days: int = Field(..., description="Number of days to workout in the week")
    current_day: str = Field(..., description="Current day of the week")
    equipment: str = Field(
        ...,
        description="Available equipment (e.g., gym, home_bodyweight, home_dumbbells)",
    )
    experience_level: ExperienceLevel = Field(
        ..., description="Fitness experience level"
    )
    user_limitations: Optional[List[str]] = Field(
        None,
        description="List of user limitations (e.g., injuries, medical conditions, mobility restrictions)",
    )
    last_week_weight_change: Optional[float] = Field(
        None, description="Weight change in kilograms last week"
    )
    previous_week_workout_plan_summary: Optional[str] = Field(
        None, description="Summary of the previous week's workout plan"
    )


class CreateMealPlanRequest(BaseModel):
    user_id: int = Field(..., description="User token")
    height: int = Field(..., description="Height in centimeters")
    weight: float = Field(..., description="Weight in kilograms")
    target_weight: float = Field(..., description="Target weight in kilograms")
    age: int = Field(..., description="Age in years")
    gender: Gender = Field(..., description="Gender")
    current_day: str = Field(..., description="Current day of the week")
    meal_plan_goal: MealPlanGoal = Field(
        ...,
        description="Primary meal plan goal",
    )
    user_remarks: Optional[str] = Field(
        None, description="Additional user remarks about the meal plan"
    )
    allergies: List[str] = Field(
        default_factory=list, description="e.g., peanut, shellfish"
    )
    intolerances: List[str] = Field(
        default_factory=list, description="e.g., lactose, gluten"
    )
    health_conditions: List[str] = Field(
        default_factory=list, description="e.g., diabetes, PCOS, thyroid, kidney"
    )
    medications: List[str] = Field(
        default_factory=list, description="Medications that affect appetite/foods"
    )
    diet_type: DietType = Field(..., description="Diet type")
    disliked_foods: List[str] = Field(default_factory=list, description="Hard no's")
    location_country: Optional[str] = Field(
        None, description="For ingredient availability and cuisine suggestions"
    )


# Response Schemas
class RequestFeasibilityResponse(BaseModel):
    feasibility: str = Field(
        ..., description="Feasibility of the request: FEASIBLE, NOT_FEASIBLE"
    )
    feasibility_reasoning: str = Field(
        ..., description="Reasoning behind the feasibility"
    )
    feasibility_recommendations: str = Field(
        ..., description="Recommendations for the request"
    )


class WorkoutPlanResponse(BaseModel):
    """Response model for workout plan generation with comprehensive fitness guidance"""

    overview: str = Field(
        ...,
        description="50 words or less, brief overview of this week's workout plan which you created, expected outcomes, user limitations considered and key training principles",
    )
    routines: List[Routine] = Field(..., description="List of routines for the week")
    weekly_schedule: List[DailySchedule] = Field(
        ..., description="List of daily workout schedules for the week"
    )
    ai_summary: str = Field(
        ...,
        description="60 words or less, summary of the week's workout plan for the AI to take a reference while generating the workout plan of next week",
    )


class MealPlanResponse(BaseModel):
    """Response model for meal plan generation with comprehensive nutrition guidance"""

    overview: str = Field(
        ...,
        description="50 words or less, brief overview of this week's meal plan which you created, expected outcomes, user limitations considered and key nutrition principles",
    )
    daily_meals: List[DailyMealPlan] = Field(..., description="List of daily meal plans for the week")
