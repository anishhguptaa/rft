"""
Workout Routes
Handles endpoints for logging workout completion
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db import get_db
from core.logger import get_logger
from api.modules.workout.services import log_workout_completion
from pydantic import BaseModel
from typing import Optional

logger = get_logger(__name__)

router = APIRouter()


# Request schema
class LogWorkoutRequest(BaseModel):
    schedule_id: int
    user_id: int
    plan_id: int
    routine_id: int
    today_weight: Optional[float] = None
    workout_notes: Optional[str] = None


# Response schema
class LogWorkoutResponse(BaseModel):
    success: bool
    message: str
    workout_history_id: int
    date: str
    is_completed: bool
    schedule_status: str

    class Config:
        from_attributes = True


@router.post("/complete", response_model=LogWorkoutResponse)
def log_workout_completion_endpoint(
    request: LogWorkoutRequest,
    db: Session = Depends(get_db),
):
    """
    Log a completed workout session.
    
    This endpoint:
    1. Creates a record in daily_user_workout_routine_history
    2. Updates the weekly_schedule status from 'started' to 'completed'
    3. Records the completion timestamp
    
    Args:
        request: LogWorkoutRequest containing:
            - schedule_id: Weekly schedule ID
            - user_id: User ID
            - plan_id: Workout plan ID
            - routine_id: Routine ID that was completed
            - today_weight: User's weight today (optional)
            - workout_notes: Notes about the workout (optional)
        
    Returns:
        Success response with workout history details
        
    Raises:
        404: If schedule not found
        400: If schedule is not in 'started' status
        
    Example:
        POST /api/workout/complete
        {
            "schedule_id": 123,
            "user_id": 456,
            "plan_id": 789,
            "routine_id": 101,
            "today_weight": 75.5,
            "workout_notes": "Great workout! Felt strong today."
        }
    """
    logger.info(f"Workout completion request for user {request.user_id}, schedule {request.schedule_id}")
    
    try:
        workout_history = log_workout_completion(
            db=db,
            schedule_id=request.schedule_id,
            user_id=request.user_id,
            plan_id=request.plan_id,
            routine_id=request.routine_id,
            today_weight=request.today_weight,
            workout_notes=request.workout_notes
        )
        
        logger.info(f"Workout completed successfully for user {request.user_id}, history ID: {workout_history.UserWorkoutRoutineHistoryId}")
        
        return LogWorkoutResponse(
            success=True,
            message="Workout completed and logged successfully",
            workout_history_id=workout_history.UserWorkoutRoutineHistoryId,
            date=workout_history.Date.isoformat(),
            is_completed=workout_history.IsCompleted,
            schedule_status="completed"
        )
    except LookupError as e:
        logger.warning(f"Workout completion failed - resource not found: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except ValueError as e:
        logger.warning(f"Workout completion failed - validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Workout completion failed with unexpected error for user {request.user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error logging workout completion: {str(e)}"
        )
