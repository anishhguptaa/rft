"""
Daily Schedule Services
Handles fetching workout plans and schedules for users
"""

from sqlalchemy.orm import Session
from models.DbModels.workout_plan import WorkoutPlan
from models.DbModels.routines import Routines
from models.DbModels.weekly_schedule import WeeklySchedule
from models.DbModels.user import User
from models.DbModels.goal import Goal
from models.DbModels.user_health_profile import UserHealthProfile
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import json
from schemas.ai_schemas import ContinueWorkoutRequest
from ai.services import AIService
from api.modules.ai_backend_integration.services import get_user_weight_history


def _format_workout_plan_response(
    db: Session,
    workout_plan: WorkoutPlan
) -> Dict[str, Any]:
    """
    Helper function to format workout plan response.
    
    Args:
        db: Database session
        workout_plan: WorkoutPlan object
        
    Returns:
        Dictionary containing formatted workout plan data
    """
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


async def _generate_first_workout_plan_for_user(
    db: Session,
    user_id: int,
    target_date: date
) -> Optional[Dict[str, Any]]:
    """
    Helper function to generate a workout plan for a user when none exists.
    
    This function:
    1. Fetches user data, goals, and health profile from the database
    2. Fetches the most recent previous workout plan summary (if any)
    3. Calculates last week's weight change from workout history
    4. Creates a ContinueWorkoutRequest with the user's information
    5. Calls the AI service to generate the workout plan
    6. Waits for the AI to generate and save the plan to the database
    7. Retrieves and returns the newly created workout plan
    
    Args:
        db: Database session
        user_id: User ID
        target_date: The date for which to generate the workout plan
        
    Returns:
        Dictionary containing the generated workout plan with routines and schedule,
        or None if generation failed
        
    Raises:
        ValueError: If user data is incomplete or AI generation fails
    """
    # Fetch user data
    user = db.query(User).filter(User.UserId == user_id).first()
    if not user:
        raise ValueError(f"User with ID {user_id} not found")
    
    # Fetch active goal
    goal = db.query(Goal).filter(
        Goal.UserId == user_id,
        Goal.Active == True
    ).first()
    if not goal:
        raise ValueError(f"No active goal found for user {user_id}. Please set up a fitness goal first.")
    
    # Fetch health profile (optional)
    health_profile = db.query(UserHealthProfile).filter(
        UserHealthProfile.UserId == user_id
    ).first()
    
    # Build user limitations list from health profile
    user_limitations = []
    if health_profile:
        if health_profile.PhysicalLimitations:
            user_limitations.extend(health_profile.PhysicalLimitations)
        if health_profile.HealthIssues:
            user_limitations.extend(health_profile.HealthIssues)
    
    # Validate required fields
    if not user.HeightCm or not user.WeightKg:
        raise ValueError(f"User {user_id} is missing required health data (height/weight)")
    
    if not goal.TargetWeight or not goal.TargetDurationInWeeks or not goal.NoOfWorkoutDaysInWeek:
        raise ValueError(f"User {user_id} has incomplete goal data. Please complete your fitness goal setup.")
    
    # Map experience level enum to string
    experience_level_map = {
        "beginner": "beginner",
        "intermediate": "intermediate",
        "advanced": "advanced"
    }
    experience_level = experience_level_map.get(
        user.UserExperienceLevel.value.lower() if user.UserExperienceLevel else "beginner",
        "beginner"
    )
    
    # Map goal type enum to workout goal
    goal_type_map = {
        "weight_loss": "weight_loss",
        "weight_gain": "weight_gain",
        "muscle_gain": "muscle_gain",
        "endurance": "endurance",
        "strength": "strength"
    }
    workout_goal = goal_type_map.get(
        goal.GoalType.value.lower() if goal.GoalType else "muscle_gain",
        "muscle_gain"
    )
    
    # Map equipment enum to string
    equipment_map = {
        "gym": "gym",
        "home_bodyweight": "home_bodyweight",
        "home_dumbbells": "home_dumbbells"
    }
    equipment = equipment_map.get(
        goal.WorkoutEquipment.value.lower() if goal.WorkoutEquipment else "gym",
        "gym"
    )
    
    # Get current day of week
    current_day = target_date.strftime("%A")
    
    # Fetch the most recent previous workout plan (ended before target_date)
    previous_workout_plan = (
        db.query(WorkoutPlan)
        .filter(
            WorkoutPlan.UserId == user_id,
            WorkoutPlan.EndDate < target_date
        )
        .order_by(WorkoutPlan.EndDate.desc())
        .first()
    )
    
    # Get the previous week's workout plan summary if it exists
    previous_week_workout_plan_summary = None
    if previous_workout_plan and previous_workout_plan.Weekly_Plan_Summary:
        previous_week_workout_plan_summary = previous_workout_plan.Weekly_Plan_Summary
    
    # Calculate last week's weight change
    last_week_weight_change = None
    try:
        weight_history = get_user_weight_history(user_id)
    except Exception as e:
        # If weight history fetch fails, continue with None
        print(f"Warning: Could not fetch weight history: {str(e)}")
    
    # Create the AI request
    ai_request = ContinueWorkoutRequest(
        user_id=user_id,
        height=int(user.HeightCm),
        weight=float(user.WeightKg),
        target_weight=float(goal.TargetWeight),
        age=user.Age,
        gender=user.Gender.lower() if user.Gender else "male",
        workout_goal=workout_goal,
        goal_timeline=goal.TargetDurationInWeeks,
        workout_days=goal.NoOfWorkoutDaysInWeek,
        current_day=current_day,
        equipment=equipment,
        experience_level=experience_level,
        user_limitations=user_limitations if user_limitations else None,
        last_week_weight_change=weight_history,
        previous_week_workout_plan_summary=previous_week_workout_plan_summary
    )
    
    # Call AI service to generate workout plan
    ai_service = AIService()
    try:
        ai_response = await ai_service.continue_workout_plan(ai_request)
        
        # Check if the AI generation was successful
        # The AI service should save the plan to the database
        # Now we need to retrieve it
        if not ai_response:
            raise ValueError("AI service failed to generate workout plan")
        
        # Wait a moment for the database to be updated (if async)
        # Then try to fetch the newly created workout plan
        workout_plan = (
            db.query(WorkoutPlan)
            .filter(
                WorkoutPlan.UserId == user_id,
                WorkoutPlan.StartDate <= target_date,
                WorkoutPlan.EndDate >= target_date
            )
            .order_by(WorkoutPlan.CreatedAt.desc())
            .first()
        )
        
        if not workout_plan:
            raise ValueError("Workout plan was generated but not found in database")
        
        # Return the workout plan using the same logic as get_user_workout_plan_by_date
        return _format_workout_plan_response(db, workout_plan)
        
    except Exception as e:
        raise ValueError(f"Failed to generate workout plan: {str(e)}")


async def get_user_workout_plan_by_date(
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
        # No workout plan exists for this user and date
        # Generate the first workout plan using AI
        try:
            return await _generate_first_workout_plan_for_user(db, user_id, target_date)
        except ValueError as e:
            # Return None if generation fails - the router will handle the error
            raise ValueError(f"Could not generate workout plan: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error generating workout plan: {str(e)}")
    # Use the helper function to format the response
    return _format_workout_plan_response(db, workout_plan)


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
    if schedule.Status == ScheduleStatus.COMPLETED:
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
    
    # Update the existing entries with swapped routine IDs
    # (Don't delete to avoid foreign key constraint violations)
    schedule_1.RoutineId = routine_id_2  # Swapped
    schedule_1.Status = ScheduleStatus.SWAPPED
    
    schedule_2.RoutineId = routine_id_1  # Swapped
    schedule_2.Status = ScheduleStatus.SWAPPED
    
    db.add(schedule_1)
    db.add(schedule_2)
    db.commit()
    db.refresh(schedule_1)
    db.refresh(schedule_2)
    
    return schedule_1, schedule_2
