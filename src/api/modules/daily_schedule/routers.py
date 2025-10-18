"""
Daily Schedule Routes
Handles endpoints for fetching user workout plans and schedules
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from core.db import get_db
from api.modules.daily_schedule.services import (
    get_user_workout_plan_by_date,
    start_workout_session,
    swap_routine_mappings
)
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date

router = APIRouter()


# Response schemas
class ExerciseResponse(BaseModel):
    name: str
    sets: int
    reps: List[int]
    weights_used: List[float]


class RoutineResponse(BaseModel):
    routine_id: int
    routine_name: str
    focus: Optional[str] = None
    exercises: List[Dict[str, Any]]


class ScheduleResponse(BaseModel):
    schedule_id: int
    day_of_week: Optional[str] = None
    routine_id: Optional[int] = None
    status: Optional[str] = None
    is_rest_day: bool
    completed_at: Optional[str] = None
    user_feedback: Optional[str] = None


class WorkoutPlanResponse(BaseModel):
    plan_id: int
    user_id: int
    generated_by_ai: bool
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    plan_version: int
    overview: Optional[str] = None
    created_at: Optional[str] = None


class UserWorkoutPlanDetailsResponse(BaseModel):
    plan: WorkoutPlanResponse
    routines: List[RoutineResponse]
    weekly_schedule: List[ScheduleResponse]


@router.get("/user/{user_id}/plan", response_model=UserWorkoutPlanDetailsResponse)
def get_user_workout_plan(
    user_id: int,
    target_date: date = Query(..., description="Date to check for workout plan (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """
    Get the workout plan assigned to a user for a specific date.
    
    Returns the complete workout plan including:
    - Plan details (overview, dates, version)
    - All routines with exercises
    - Weekly schedule with status
    
    Args:
        user_id: User ID
        target_date: Date to check for workout plan (format: YYYY-MM-DD)
        
    Returns:
        Complete workout plan details with routines and schedule
        
    Example:
        GET /api/daily-schedule/user/123/plan?target_date=2025-10-18
    """
    try:
        result = get_user_workout_plan_by_date(
            db=db,
            user_id=user_id,
            target_date=target_date
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No workout plan found for user {user_id} on date {target_date}"
            )
        
        return result
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Catch any other errors and return detailed message
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching workout plan: {str(e)}"
        )


# Response schema for start session
class StartWorkoutSessionResponse(BaseModel):
    success: bool
    message: str
    schedule_id: int
    new_status: str


@router.post("/session/{schedule_id}/start", response_model=StartWorkoutSessionResponse)
def start_workout_session_endpoint(
    schedule_id: int,
    db: Session = Depends(get_db),
):
    """
    Start a workout session by changing status from 'pending' to 'started'.
    
    This endpoint updates the status of a weekly schedule entry to indicate
    that the user has started their workout.
    
    Args:
        schedule_id: The weekly schedule ID (schedule_id from weekly_schedule table)
        
    Returns:
        Success response with updated status
        
    Raises:
        404: If schedule not found
        400: If session is not in pending status
        
    Example:
        POST /api/daily-schedule/session/123/start
    """
    try:
        schedule = start_workout_session(db=db, schedule_id=schedule_id)
        
        if not schedule:
            raise HTTPException(
                status_code=404,
                detail=f"Workout session with schedule_id {schedule_id} not found"
            )
        
        return StartWorkoutSessionResponse(
            success=True,
            message="Workout session started successfully",
            schedule_id=schedule.ScheduleId,
            new_status=schedule.Status.value if hasattr(schedule.Status, 'value') else str(schedule.Status)
        )
    except ValueError as e:
        # Status validation error
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting workout session: {str(e)}"
        )


# Request and Response schemas for swap routines
class SwapRoutinesRequest(BaseModel):
    schedule_id_1: int
    schedule_id_2: int


class SwapRoutinesResponse(BaseModel):
    success: bool
    message: str
    schedule_1: ScheduleResponse
    schedule_2: ScheduleResponse


@router.post("/swap-routines", response_model=SwapRoutinesResponse)
def swap_routines_endpoint(
    request: SwapRoutinesRequest,
    db: Session = Depends(get_db),
):
    """
    Swap routine mappings between two weekly schedule entries.
    
    This endpoint:
    1. Fetches both schedule entries
    2. Deletes the existing entries (soft delete)
    3. Creates new entries with swapped routine IDs
    4. Sets the status of new entries to 'swapped'
    
    Args:
        request: SwapRoutinesRequest containing:
            - schedule_id_1: First weekly schedule ID
            - schedule_id_2: Second weekly schedule ID
        
    Returns:
        Success response with both new schedule entries
        
    Raises:
        404: If either schedule not found
        
    Example:
        POST /api/daily-schedule/swap-routines
        {
            "schedule_id_1": 123,
            "schedule_id_2": 456
        }
    """
    try:
        new_schedule_1, new_schedule_2 = swap_routine_mappings(
            db=db,
            schedule_id_1=request.schedule_id_1,
            schedule_id_2=request.schedule_id_2
        )
        
        # Format schedule responses
        schedule_1_response = ScheduleResponse(
            schedule_id=new_schedule_1.ScheduleId,
            day_of_week=new_schedule_1.DayOfWeek.value if new_schedule_1.DayOfWeek else None,
            routine_id=new_schedule_1.RoutineId,
            status=new_schedule_1.Status.value if new_schedule_1.Status else None,
            is_rest_day=new_schedule_1.IsRestDay,
            completed_at=new_schedule_1.CompletedAt.isoformat() if new_schedule_1.CompletedAt else None,
            user_feedback=new_schedule_1.UserFeedback
        )
        
        schedule_2_response = ScheduleResponse(
            schedule_id=new_schedule_2.ScheduleId,
            day_of_week=new_schedule_2.DayOfWeek.value if new_schedule_2.DayOfWeek else None,
            routine_id=new_schedule_2.RoutineId,
            status=new_schedule_2.Status.value if new_schedule_2.Status else None,
            is_rest_day=new_schedule_2.IsRestDay,
            completed_at=new_schedule_2.CompletedAt.isoformat() if new_schedule_2.CompletedAt else None,
            user_feedback=new_schedule_2.UserFeedback
        )
        
        return SwapRoutinesResponse(
            success=True,
            message="Routines swapped successfully",
            schedule_1=schedule_1_response,
            schedule_2=schedule_2_response
        )
    except LookupError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error swapping routines: {str(e)}"
        )
