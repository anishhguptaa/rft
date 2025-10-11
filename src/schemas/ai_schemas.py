"""
AI Schemas
Pydantic models for AI endpoints
"""

from pydantic import BaseModel, Field
from typing import List


class CreateCompleteWorkoutRequest(BaseModel):
    height: float = Field(..., description="Height in centimeters")
    weight: float = Field(..., description="Weight in kilograms")
    age: int = Field(..., description="Age in years")
    gender: str = Field(..., description="Gender (male/female/other)")
    workout_goal: str = Field(
        ...,
        description="Primary workout goal (e.g., weight_loss, weight_gain, weight_loss_with_muscle_gain)",
    )
    goal_timeline: int = Field(..., description="Target goal timeline in weeks")
    workout_days: int = Field(..., description="Number of days to workout in the week")
    current_day: str = Field(..., description="Current day of the week")
    equipment: str = Field(
        ...,
        description="Available equipment (e.g., gym, home_bodyweight, home_dumbbells)",
    )
    experience_level: str = Field(
        ..., description="Fitness experience level (beginner/intermediate/advanced)"
    )


class Exercise(BaseModel):
    """Individual exercise model"""

    name: str = Field(..., description="Name of the exercise")
    sets: int = Field(..., description="Number of sets")
    reps: str = Field(
        ..., description="Number of repetitions (can be a range like '8-12')"
    )
    rest_period: str = Field(..., description="Rest period between sets")
    difficulty: str = Field(
        ..., description="Difficulty level (beginner/intermediate/advanced)"
    )
    equipment: str = Field(..., description="Equipment needed for the exercise")
    form_tips: str = Field(..., description="Tips for proper form")


class WorkoutDay(BaseModel):
    """Model for a single workout day"""

    focus: str = Field(
        ..., description="Primary focus of the workout (e.g., 'Upper Body', 'Cardio')"
    )
    exercises: List[Exercise] = Field(..., description="List of exercises for this day")


class WeeklySchedule(BaseModel):
    """Model for weekly workout schedule"""

    number_of_days: int = Field(..., description="Number of workout days in the week")
    daily_schedule: List[WorkoutDay] = Field(..., description="List of workout days")


class WorkoutPlanResponse(BaseModel):
    """Response model for workout plan generation"""

    overview: str = Field(..., description="Brief overview of the workout plan")
    weekly_schedule: WeeklySchedule = Field(..., description="Weekly workout schedule")
