"""
AI Backend Integration Routes
Handles endpoints for saving AI-generated workout plans
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db import get_db
from api.modules.ai_backend_integration.services import save_ai_workout_plan
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


# Request schemas
class ExerciseData(BaseModel):
    name: str
    sets: int
    reps: List[int]
    weights_used: List[float]


class RoutineData(BaseModel):
    name: str
    focus: str
    exercises: List[ExerciseData]


class ScheduleData(BaseModel):
    day_of_week: str
    routine_name: Optional[str] = None
    status: str = "pending"


class SaveWorkoutPlanRequest(BaseModel):
    user_id: int
    routines: List[RoutineData]
    weekly_schedule: List[ScheduleData]
    ai_summary: str


# Response schema
class SaveWorkoutPlanResponse(BaseModel):
    success: bool
    message: str
    plan_id: Optional[int] = None

    class Config:
        from_attributes = True


@router.post("/save-workout-plan", response_model=SaveWorkoutPlanResponse)
def save_workout_plan_endpoint(
    request: SaveWorkoutPlanRequest,
    db: Session = Depends(get_db),
):
    """
    Save AI-generated workout plan to database.
    
    Creates records in workout_plans, routines, and weekly_schedule tables.
    Automatically sets start_date to current week's Monday and end_date to Sunday.
    
    Request body should contain:
    - user_id: User ID
    - routines: List of routines with exercises
    - weekly_schedule: List of daily schedule entries
    - ai_summary: AI-generated summary
    """
    try:
        # Call the service function
        workout_plan = save_ai_workout_plan(
            db=db,
            user_id=request.user_id,
            ai_response=request  # Pass the request object which has the required attributes
        )
        
        return SaveWorkoutPlanResponse(
            success=True,
            message="Workout plan saved successfully",
            plan_id=workout_plan.PlanId
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save workout plan: {str(e)}"
        )
