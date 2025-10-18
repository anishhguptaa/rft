"""
AI Schemas
Pydantic models for AI endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Optional


# Helper Schemas
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
class CreateCompleteWorkoutRequest(BaseModel):
    user_token: str = Field(..., description="User token")
    first_workout: bool = Field(
        ..., description="Whether it is the first workout plan or not"
    )
    height: int = Field(..., description="Height in centimeters")
    weight: float = Field(..., description="Weight in kilograms")
    target_weight: float = Field(
        ..., description="Target weight in kilograms"
    )
    age: int = Field(..., description="Age in years")
    gender: str = Field(..., description="Gender (male/female/other)")
    workout_goal: str = Field(
        ...,
        description="Primary workout goal (e.g., weight_loss, weight_gain, muscle_gain, endurance, strength)",
    )
    goal_timeline: int = Field(
        ..., description="Target goal timeline in weeks"
    )
    workout_days: int = Field(
        ..., description="Number of days to workout in the week"
    )
    current_day: str = Field(..., description="Current day of the week")
    equipment: str = Field(
        ...,
        description="Available equipment (e.g., gym, home_bodyweight, home_dumbbells)",
    )
    experience_level: str = Field(
        ..., description="Fitness experience level (beginner/intermediate/advanced)"
    )
    user_limitations: Optional[List[str]] = Field(
        None,
        description="List of user limitations (e.g., injuries, medical conditions, mobility restrictions)",
    )
    user_remarks: Optional[str] = Field(
        None, description="Additional user remarks about the workout plan"
    )


class AdjustWorkoutPlanRequest(BaseModel):
    user_token: str = Field(..., description="User token")
    remaining_routines: List[Routine] = Field(..., description="List of remaining routines for the week")
    current_day: str = Field(..., description="Current day of the week")


# class EditDailyWorkoutPlanRequest(BaseModel):
#     edit_plan: str = Field(
#         ...,
#         description="What kind of changes the user wants to make to the daily workout plan",
#     )
#     daily_workout_plan: WorkoutDay = Field(
#         ..., description="Daily workout plan to edit"
#     )


# class EditWeeklyWorkoutPlanRequest(BaseModel):
#     user_id: int = Field(..., description="User ID")
#     weekly_workout_plan: WeeklySchedule = Field(..., description="Weekly workout plan to edit")


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
