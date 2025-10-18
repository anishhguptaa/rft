"""
AI Backend Integration Services
Handles saving AI-generated workout plans to the database
"""

from sqlalchemy.orm import Session
from models.DbModels.workout_plan import WorkoutPlan
from models.DbModels.routines import Routines
from models.DbModels.weekly_schedule import WeeklySchedule
from models.Enums.enums import DayOfWeek, ScheduleStatus
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json


def save_ai_workout_plan(
    db: Session,
    user_id: int,
    ai_response: Any  # Changed to Any to accept object with attributes
) -> WorkoutPlan:
    """
    Save AI-generated workout plan to database.
    
    Parses the AI response object and creates records in:
    - workout_plans table
    - routines table
    - weekly_schedule table
    
    Automatically calculates start_date and end_date as the current week's
    Monday (start) and Sunday (end).
    
    Args:
        db: Database session
        user_id: User ID for whom the plan is created
        ai_response: AI response object with attributes:
            - routines: List of routine objects
            - weekly_schedule: List of schedule objects
            - ai_summary: String summary
        
    Returns:
        WorkoutPlan: The created workout plan object
    """
    
    # Calculate current week's start (Monday) and end (Sunday) dates
    today = datetime.now().date()
    # Get the weekday (0=Monday, 6=Sunday)
    weekday = today.weekday()
    # Calculate Monday of current week
    start_date = today - timedelta(days=weekday)
    # Calculate Sunday of current week (6 days after Monday)
    end_date = start_date + timedelta(days=6)
    
    # Extract data from AI response object (using attributes instead of dict methods)
    routines_data = getattr(ai_response, "routines", [])
    weekly_schedule_data = getattr(ai_response, "weekly_schedule", [])
    ai_summary = getattr(ai_response, "ai_summary", "")
    
    # Step 1: Create WorkoutPlan
    workout_plan = WorkoutPlan(
        UserId=user_id,
        GeneratedByAI=True,
        StartDate=start_date,
        EndDate=end_date,
        PlanVersion=1,
        Overview=ai_summary
    )
    db.add(workout_plan)
    db.flush()  # Flush to get the PlanId without committing
    
    # Step 2: Create Routines and map routine names to IDs
    routine_name_to_id = {}
    
    for routine_data in routines_data:
        routine_name = getattr(routine_data, "name", None)
        routine_focus = getattr(routine_data, "focus", None)
        
        # Convert the entire routine object to dict for JSON serialization
        # This handles Pydantic models properly
        if hasattr(routine_data, "dict"):
            # Pydantic v1
            routine_dict = routine_data.dict()
        elif hasattr(routine_data, "model_dump"):
            # Pydantic v2
            routine_dict = routine_data.model_dump()
        else:
            # Fallback: try to convert to dict manually
            routine_dict = {
                "name": routine_name,
                "focus": routine_focus,
                "exercises": [
                    ex.model_dump() if hasattr(ex, "model_dump") else ex.dict() if hasattr(ex, "dict") else ex
                    for ex in getattr(routine_data, "exercises", [])
                ]
            }
        
        # Convert entire routine object to JSON string
        routine_json = json.dumps(routine_dict)
        
        routine = Routines(
            PlanId=workout_plan.PlanId,
            RoutineName=routine_name,
            Focus=routine_focus,
            RoutineJson=routine_json
        )
        db.add(routine)
        db.flush()  # Flush to get the RoutineId
        
        # Map routine name to ID for weekly schedule
        routine_name_to_id[routine_name] = routine.RoutineId
    
    # Step 3: Create WeeklySchedule entries
    for schedule_data in weekly_schedule_data:
        day_of_week_str = getattr(schedule_data, "day_of_week", None)
        routine_name = getattr(schedule_data, "routine_name", None)
        status_str = getattr(schedule_data, "status", "pending")
        
        # Convert day string to enum
        try:
            day_of_week = DayOfWeek[day_of_week_str.upper()]
        except (KeyError, AttributeError):
            # Default to Monday if invalid
            day_of_week = DayOfWeek.MONDAY
        
        # Convert status string to enum
        try:
            status = ScheduleStatus[status_str.upper()]
        except (KeyError, AttributeError):
            status = ScheduleStatus.PENDING
        
        # Get routine ID from name
        routine_id = routine_name_to_id.get(routine_name)
        
        weekly_schedule = WeeklySchedule(
            PlanId=workout_plan.PlanId,
            DayOfWeek=day_of_week,
            RoutineId=routine_id,
            Status=status,
            IsRestDay=(routine_id is None)  # If no routine, it's a rest day
        )
        db.add(weekly_schedule)
    
    # Commit all changes
    db.commit()
    db.refresh(workout_plan)
    
    return workout_plan


def get_workout_plan_with_details(
    db: Session,
    plan_id: int
) -> Dict[str, Any]:
    """
    Retrieve a workout plan with all its routines and weekly schedule.
    
    Args:
        db: Database session
        plan_id: Workout plan ID
        
    Returns:
        Dict containing the plan, routines, and weekly schedule
    """
    # Get workout plan
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.PlanId == plan_id).first()
    if not plan:
        return None
    
    # Get routines
    routines = db.query(Routines).filter(Routines.PlanId == plan_id).all()
    
    # Get weekly schedule
    weekly_schedule = db.query(WeeklySchedule).filter(WeeklySchedule.PlanId == plan_id).all()
    
    return {
        "plan": plan,
        "routines": routines,
        "weekly_schedule": weekly_schedule
    }
