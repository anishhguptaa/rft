"""
AI Schemas
Pydantic models for AI endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Optional

# Request Schemas
class CreateCompleteWorkoutRequest(BaseModel):
    height: int = Field(..., description="Height in centimeters", ge=100, le=250)
    weight: float = Field(..., description="Weight in kilograms", gt=0, le=200)
    target_weight: float = Field(..., description="Target weight in kilograms", gt=0, le=200)
    age: int = Field(..., description="Age in years", ge=13, le=100)
    gender: str = Field(..., description="Gender (male/female/other)")
    workout_goal: str = Field(
        ...,
        description="Primary workout goal (e.g., weight_loss, weight_gain, muscle_gain, endurance, strength)",
    )
    goal_timeline: int = Field(..., description="Target goal timeline in weeks", ge=1, le=52)
    workout_days: int = Field(..., description="Number of days to workout in the week", ge=1, le=7)
    current_day: str = Field(..., description="Current day of the week")
    equipment: str = Field(
        ...,
        description="Available equipment (e.g., gym, home_bodyweight, home_dumbbells)",
    )
    experience_level: str = Field(
        ..., description="Fitness experience level (beginner/intermediate/advanced)"
    )
    user_limitations: list[str] = Field(
        ..., description="List of user limitations (e.g., injuries, medical conditions, mobility restrictions)"
    )
    user_remarks: Optional[str] = Field(None, description="Additional user remarks about the workout plan")

# class EditWeeklyWorkoutPlanRequest(BaseModel):
#     user_id: int = Field(..., description="User ID")
#     weekly_workout_plan: WeeklySchedule = Field(..., description="Weekly workout plan to edit")

# class EditDailyWorkoutPlanRequest(BaseModel):
#     user_id: int = Field(..., description="User ID")
#     daily_workout_plan: WorkoutDay = Field(..., description="Daily workout plan to edit")


# Response Schemas
class RequestFeasibilityResponse(BaseModel):
    feasibility: str = Field(..., description="Feasibility of the request: FEASIBLE, NOT_FEASIBLE")
    feasibility_reasoning: str = Field(..., description="Reasoning behind the feasibility")
    feasibility_recommendations: str = Field(..., description="Recommendations for the request")

class Reps(BaseModel):
    weight_used: float = Field(..., description="Weight used for the exercise in kilograms", ge=0, le=1000)
    number_of_reps: str = Field(
        ..., description="Number of repetitions (Must be a specific number like '10' or '12)"
    )

class Exercise(BaseModel):
    """Individual exercise model with comprehensive details for workout execution"""

    name: str = Field(..., description="Specific name of the exercise (e.g., 'Barbell Back Squat', 'Push-ups')")
    number_of_sets: int = Field(..., description="Number of sets to perform", ge=1, le=10)
    reps: List[Reps] = Field(..., description="List of reps with weights for each set")


class WorkoutDay(BaseModel):
    """Model for a single workout day with focused training objectives"""

    focus: str = Field(
        ..., description="Primary focus of the workout (e.g., 'Upper Body Strength', 'Lower Body Hypertrophy', 'Cardio Endurance')"
    )
    day_of_week: str = Field(..., description="Day of the week")
    exercises: List[Exercise] = Field(..., description="List of exercises for this day (typically 6-8 exercises)")


class WeeklySchedule(BaseModel):
    """Model for weekly workout schedule with progressive structure"""

    number_of_days: int = Field(..., description="Number of workout days in the week", ge=1, le=7)
    daily_schedule: List[WorkoutDay] = Field(..., description="List of workout days with their respective exercises")


class WorkoutPlanResponse(BaseModel):
    """Response model for workout plan generation with comprehensive fitness guidance"""

    overview: str = Field(..., description="50 words or less, brief overview of this week's workout plan which you created, expected outcomes, user limitations considered and key training principles")
    weekly_schedule: WeeklySchedule = Field(..., description="Weekly workout schedule with detailed exercise programming")
    summary: str = Field(..., description="60 words or less, summary of the week's workout plan for the AI to take a reference while generating the workout plan of next week")
