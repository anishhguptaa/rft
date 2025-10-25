"""
AI Backend Integration Services
Handles saving AI-generated workout plans to the database
"""

from sqlalchemy.orm import Session
from models.DbModels.workout_plan import WorkoutPlan
from models.DbModels.routines import Routines
from models.DbModels.weekly_schedule import WeeklySchedule
from models.DbModels.user import User
from models.DbModels.daily_user_workout_routine_history import DailyUserWorkoutRoutineHistory
from models.Enums.enums import DayOfWeek, ScheduleStatus
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
from core.db import SessionLocal
import json


def save_ai_workout_plan(
    ai_response: Any  # AI response object with user_id and other attributes
) -> WorkoutPlan:
    """
    Save AI-generated workout plan to database.
    
    Creates its own database session and manages the transaction.
    
    Parses the AI response object and creates records in:
    - workout_plans table
    - routines table
    - weekly_schedule table
    
    Automatically calculates start_date and end_date as the current week's
    Monday (start) and Sunday (end).
    
    Args:
        ai_response: AI response object with attributes:
            - user_id: User ID for whom the plan is created
            - routines: List of routine objects
            - weekly_schedule: List of schedule objects
            - overview: String summary/overview
        
    Returns:
        WorkoutPlan: The created workout plan object
    """
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Extract user_id from AI response
        user_id = getattr(ai_response, "user_id", None)
        if not user_id:
            raise ValueError("user_id is required in ai_response")
        
        # Calculate current week's start (Monday) and end (Sunday) dates
        today = datetime.now().date()
        # Get the weekday (0=Monday, 6=Sunday)
        weekday = today.weekday()
        # Calculate Monday of current week
        start_date = today - timedelta(days=weekday)
        # Calculate Sunday of current week (6 days after Monday)
        end_date = start_date + timedelta(days=6)
        
        # Check if a workout plan already exists for this user in the date range
        existing_plan = (
            db.query(WorkoutPlan)
            .filter(
                WorkoutPlan.UserId == user_id,
                WorkoutPlan.IsActive == True,
                WorkoutPlan.StartDate <= end_date,
                WorkoutPlan.EndDate >= start_date
            )
            .first()
        )
        
        # If an existing active plan is found, deactivate it
        if existing_plan:
            existing_plan.IsActive = False
            db.add(existing_plan)
            db.flush()  # Flush to persist the deactivation
        
        # Extract data from AI response object (using attributes instead of dict methods)
        routines_data = getattr(ai_response, "routines", [])
        weekly_schedule_data = getattr(ai_response, "weekly_schedule", [])
        overview = getattr(ai_response, "overview", "")
        
        # Step 1: Create WorkoutPlan
        workout_plan = WorkoutPlan(
            UserId=user_id,
            GeneratedByAI=True,
            StartDate=start_date,
            EndDate=end_date,
            PlanVersion=1,
            Overview=overview
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
    
    finally:
        # Always close the database session
        db.close()


def save_ai_meal_plan(
    user_id: int,
    ai_meal_response_json: str
) -> Dict[str, Any]:
    """
    Save AI-generated meal plan to the workout plan table.
    
    Finds the active workout plan for the user where today's date falls
    within the plan's date range (StartDate to EndDate), and updates
    the MealJson column with the provided meal plan JSON.
    
    Args:
        user_id: User ID for whom the meal plan is being saved
        ai_meal_response_json: JSON string containing the AI-generated meal plan
        
    Returns:
        Dict with success status and message:
        - success: True if meal plan was saved, False otherwise
        - message: Description of the result
        - plan_id: The workout plan ID (if successful)
    """
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Get today's date
        today = datetime.now().date()
        
        # Find the workout plan where today's date is within the date range
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
        
        # If no workout plan found for the current date range
        if not workout_plan:
            return {
                "success": False,
                "message": f"No active workout plan found for user {user_id} covering today's date ({today})",
                "plan_id": None
            }
        
        # Update the MealJson column with the AI-generated meal plan
        workout_plan.MealJson = ai_meal_response_json
        
        # Commit the changes
        db.commit()
        db.refresh(workout_plan)
        
        return {
            "success": True,
            "message": f"Meal plan successfully saved to workout plan {workout_plan.PlanId}",
            "plan_id": workout_plan.PlanId
        }
    
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"Failed to save meal plan: {str(e)}",
            "plan_id": None
        }
    
    finally:
        # Always close the database session
        db.close()


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


def get_user_weight_history(user_id: int) -> Dict[str, Any]:
    """
    Get user's current weight and last week's weight history.
    
    Creates its own database session and manages the transaction.
    
    Retrieves:
    - Current weight from user table
    - Last week's weight logged during workouts (Monday to Sunday)
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary containing:
        - CurrentWeight: User's current weight
        - LastWeekWeight: Dictionary mapping day names to weights
        
    Example return:
        {
            "CurrentWeight": 58.5,
            "LastWeekWeight": {
                "Monday": 55.0,
                "Tuesday": 56.0,
                "Wednesday": 57.0,
                "Thursday": None,
                "Friday": 58.0,
                "Saturday": None,
                "Sunday": 58.5
            }
        }
    """
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Get user's current weight
        user = db.query(User).filter(User.UserId == user_id).first()
        current_weight = user.CurrentWeight if user else None
        
        # Calculate last week's date range (Monday to Sunday)
        today = date.today()
        # Get days since last Monday
        days_since_monday = today.weekday()
        # Calculate last week's Monday (7 days before this week's Monday)
        last_week_monday = today - timedelta(days=days_since_monday + 7)
        # Calculate last week's Sunday
        last_week_sunday = last_week_monday + timedelta(days=6)
        
        # Get workout history for last week
        workout_history = (
            db.query(DailyUserWorkoutRoutineHistory)
            .filter(
                DailyUserWorkoutRoutineHistory.UserId == user_id,
                DailyUserWorkoutRoutineHistory.Date >= last_week_monday,
                DailyUserWorkoutRoutineHistory.Date <= last_week_sunday,
                DailyUserWorkoutRoutineHistory.IsCompleted == True
            )
            .order_by(DailyUserWorkoutRoutineHistory.Date)
            .all()
        )
        
        # Create a dictionary mapping dates to weights
        date_to_weight = {
            workout.Date: workout.TodayWeight
            for workout in workout_history
            if workout.TodayWeight is not None
        }
        
        # Build last week's weight dictionary with day names
        last_week_weight = {}
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for i, day_name in enumerate(day_names):
            day_date = last_week_monday + timedelta(days=i)
            last_week_weight[day_name] = date_to_weight.get(day_date)
        
        return {
            "CurrentWeight": current_weight,
            "LastWeekWeight": last_week_weight
        }
    
    finally:
        # Always close the database session
        db.close()
