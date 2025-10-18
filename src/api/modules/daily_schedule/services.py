"""
Daily Schedule Services
Handles fetching workout plans and schedules for users
"""

from sqlalchemy.orm import Session
from models.DbModels.workout_plan import WorkoutPlan
from models.DbModels.routines import Routines
from models.DbModels.weekly_schedule import WeeklySchedule
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import json


def get_user_workout_plan_by_date(
    db: Session,
    user_id: int,
    target_date: date
) -> Optional[Dict[str, Any]]:
    """
    Get the workout plan assigned to a user for a specific date.
    
    Fetches the workout plan that covers the target date, along with
    all associated routines and weekly schedule.
    
    Args:
        db: Database session
        user_id: User ID
        target_date: The date to check for workout plan
        
    Returns:
        Dictionary containing:
        - plan: WorkoutPlan details
        - routines: List of routines with exercises
        - weekly_schedule: List of weekly schedule entries
        
        Returns None if no plan found for the date.
    """
    
    # Find workout plan that covers the target date
    workout_plan = (
        db.query(WorkoutPlan)
        .filter(
            WorkoutPlan.UserId == user_id,
            WorkoutPlan.StartDate <= target_date,
            WorkoutPlan.EndDate >= target_date
        )
        .order_by(WorkoutPlan.CreatedAt.desc())  # Get most recent if multiple
        .first()
    )
    
    if not workout_plan:
        return None
    
    # Get all routines for this plan
    routines = (
        db.query(Routines)
        .filter(Routines.PlanId == workout_plan.PlanId)
        .all()
    )
    
    # Get weekly schedule for this plan
    weekly_schedule = (
        db.query(WeeklySchedule)
        .filter(WeeklySchedule.PlanId == workout_plan.PlanId)
        .all()
    )
    
    # Parse routine JSON data
    routines_list = []
    for routine in routines:
        try:
            # Parse the JSON string
            routine_json_data = json.loads(routine.RoutineJson) if routine.RoutineJson else {}
            
            # Check if the JSON contains the full routine object or just exercises
            if isinstance(routine_json_data, dict) and "exercises" in routine_json_data:
                # JSON contains full routine object, extract exercises
                exercises = routine_json_data.get("exercises", [])
            elif isinstance(routine_json_data, list):
                # JSON is already a list of exercises
                exercises = routine_json_data
            else:
                exercises = []
        except (json.JSONDecodeError, TypeError):
            exercises = []
        
        routine_dict = {
            "routine_id": routine.RoutineId,
            "routine_name": routine.RoutineName,
            "focus": routine.Focus,
            "exercises": exercises
        }
        routines_list.append(routine_dict)
    
    # Format weekly schedule data
    schedule_list = []
    for schedule in weekly_schedule:
        # Handle enum values safely
        day_of_week_value = None
        if schedule.DayOfWeek:
            day_of_week_value = schedule.DayOfWeek.value if hasattr(schedule.DayOfWeek, 'value') else str(schedule.DayOfWeek)
        
        status_value = None
        if schedule.Status:
            status_value = schedule.Status.value if hasattr(schedule.Status, 'value') else str(schedule.Status)
        
        schedule_dict = {
            "schedule_id": schedule.ScheduleId,
            "day_of_week": day_of_week_value,
            "routine_id": schedule.RoutineId,
            "status": status_value,
            "is_rest_day": schedule.IsRestDay,
            "completed_at": schedule.CompletedAt.isoformat() if schedule.CompletedAt else None,
            "user_feedback": schedule.UserFeedback
        }
        schedule_list.append(schedule_dict)
    
    # Format workout plan data
    plan_dict = {
        "plan_id": workout_plan.PlanId,
        "user_id": workout_plan.UserId,
        "generated_by_ai": workout_plan.GeneratedByAI,
        "start_date": workout_plan.StartDate.isoformat() if workout_plan.StartDate else None,
        "end_date": workout_plan.EndDate.isoformat() if workout_plan.EndDate else None,
        "plan_version": workout_plan.PlanVersion,
        "overview": workout_plan.Overview,
        "created_at": workout_plan.CreatedAt.isoformat() if workout_plan.CreatedAt else None
    }
    
    return {
        "plan": plan_dict,
        "routines": routines_list,
        "weekly_schedule": schedule_list
    }


def start_workout_session(
    db: Session,
    schedule_id: int
) -> Optional[WeeklySchedule]:
    """
    Start a workout session by changing status from pending to started.
    
    Args:
        db: Database session
        schedule_id: Weekly schedule ID
        
    Returns:
        Updated WeeklySchedule object, or None if not found
        
    Raises:
        ValueError: If the session is not in pending status
    """
    from models.Enums.enums import ScheduleStatus
    
    # Find the schedule entry
    schedule = db.query(WeeklySchedule).filter(WeeklySchedule.ScheduleId == schedule_id).first()
    
    if not schedule:
        return None
    
    # Check if status is pending
    if schedule.Status != ScheduleStatus.PENDING:
        raise ValueError(f"Cannot start session. Current status is '{schedule.Status.value}', expected 'pending'")
    
    # Update status to started
    schedule.Status = ScheduleStatus.STARTED
    
    db.commit()
    db.refresh(schedule)
    
    return schedule


def swap_routine_mappings(
    db: Session,
    schedule_id_1: int,
    schedule_id_2: int
) -> tuple[WeeklySchedule, WeeklySchedule]:
    """
    Swap routine mappings between two weekly schedule entries.
    
    This function:
    1. Fetches both schedule entries
    2. Soft deletes the existing entries (marks them as inactive)
    3. Creates new entries with swapped routine IDs
    4. Sets the status of new entries to 'swapped'
    
    Args:
        db: Database session
        schedule_id_1: First weekly schedule ID
        schedule_id_2: Second weekly schedule ID
        
    Returns:
        Tuple of (new_schedule_1, new_schedule_2) with swapped routines
        
    Raises:
        LookupError: If either schedule not found
    """
    from models.Enums.enums import ScheduleStatus
    
    # Fetch both schedule entries
    schedule_1 = db.query(WeeklySchedule).filter(WeeklySchedule.ScheduleId == schedule_id_1).first()
    schedule_2 = db.query(WeeklySchedule).filter(WeeklySchedule.ScheduleId == schedule_id_2).first()
    
    if not schedule_1:
        raise LookupError(f"Schedule with ID {schedule_id_1} not found")
    if not schedule_2:
        raise LookupError(f"Schedule with ID {schedule_id_2} not found")
    
    # Store the routine IDs before swapping
    routine_id_1 = schedule_1.RoutineId
    routine_id_2 = schedule_2.RoutineId
    
    # Soft delete the existing entries by removing them
    # (We'll create new entries instead of updating to maintain history)
    db.delete(schedule_1)
    db.delete(schedule_2)
    db.flush()
    
    # Create new schedule entries with swapped routine IDs
    new_schedule_1 = WeeklySchedule(
        PlanId=schedule_1.PlanId,
        DayOfWeek=schedule_1.DayOfWeek,
        RoutineId=routine_id_2,  # Swapped
        Status=ScheduleStatus.SWAPPED,
        IsRestDay=schedule_1.IsRestDay,
        UserFeedback=schedule_1.UserFeedback
    )
    
    new_schedule_2 = WeeklySchedule(
        PlanId=schedule_2.PlanId,
        DayOfWeek=schedule_2.DayOfWeek,
        RoutineId=routine_id_1,  # Swapped
        Status=ScheduleStatus.SWAPPED,
        IsRestDay=schedule_2.IsRestDay,
        UserFeedback=schedule_2.UserFeedback
    )
    
    db.add(new_schedule_1)
    db.add(new_schedule_2)
    db.commit()
    db.refresh(new_schedule_1)
    db.refresh(new_schedule_2)
    
    return new_schedule_1, new_schedule_2
