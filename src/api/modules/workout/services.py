"""
Workout Services
Handles logging workout data and updating workout status
"""

from sqlalchemy.orm import Session
from models.DbModels.daily_user_workout_routine_history import DailyUserWorkoutRoutineHistory
from models.DbModels.weekly_schedule import WeeklySchedule
from models.DbModels.user import User
from models.Enums.enums import ScheduleStatus
from core.logger import get_logger
from datetime import date, datetime
from typing import Optional

logger = get_logger(__name__)


def log_workout_completion(
    db: Session,
    schedule_id: int,
    user_id: int,
    plan_id: int,
    routine_id: int,
    today_weight: Optional[float] = None,
    workout_notes: Optional[str] = None
) -> DailyUserWorkoutRoutineHistory:
    """
    Log a completed workout and update the weekly schedule status to completed.
    
    Creates a record in daily_user_workout_routine_history and updates
    the weekly_schedule status from 'started' to 'completed'.
    
    Args:
        db: Database session
        schedule_id: Weekly schedule ID
        user_id: User ID
        plan_id: Workout plan ID
        routine_id: Routine ID
        today_weight: User's weight today (optional)
        workout_notes: Notes about the workout (optional)
        
    Returns:
        DailyUserWorkoutRoutineHistory: The created workout history record
        
    Raises:
        LookupError: If schedule or user not found
        ValueError: If schedule is not in 'started' status
    """
    logger.info(f"Starting workout completion for user {user_id}, schedule {schedule_id}")
    
    # Validate that the user exists
    user = db.query(User).filter(User.UserId == user_id).first()
    if not user:
        logger.error(f"User not found: {user_id}")
        raise LookupError(f"User with ID {user_id} not found")
    
    logger.debug(f"User found: {user.Email}")
    
    # Find the schedule entry
    schedule = db.query(WeeklySchedule).filter(WeeklySchedule.ScheduleId == schedule_id).first()
    
    if not schedule:
        logger.error(f"Schedule not found: {schedule_id}")
        raise LookupError(f"Schedule with ID {schedule_id} not found")
    
    logger.debug(f"Schedule found with status: {schedule.Status.value}")
    
    # Validate that the schedule is in 'started' status
    if schedule.Status != ScheduleStatus.STARTED:
        logger.warning(f"Cannot complete workout - schedule status is {schedule.Status.value}, expected 'started'")
        raise ValueError(
            f"Cannot complete workout. Current status is '{schedule.Status.value}', expected 'started'"
        )
    
    # Create workout history record
    workout_history = DailyUserWorkoutRoutineHistory(
        PlanId=plan_id,
        RoutineId=routine_id,
        ScheduleId=schedule_id,
        UserId=user_id,
        Date=date.today(),
        IsCompleted=True,
        TodayWeight=today_weight,
        WorkoutNotes=workout_notes
    )
    
    logger.debug(f"Created workout history record for plan {plan_id}, routine {routine_id}")
    
    # Update user weight if provided
    if today_weight:
        user.CurrentWeight = today_weight
        db.add(user)
        logger.debug(f"Updated user weight to {today_weight}")
    
    db.add(workout_history)
    
    # Update schedule status to completed
    schedule.Status = ScheduleStatus.COMPLETED
    schedule.CompletedAt = datetime.now()
    
    db.add(schedule)
    db.commit()
    db.refresh(workout_history)
    db.refresh(schedule)
    
    logger.info(f"Workout completion successful - history ID: {workout_history.UserWorkoutRoutineHistoryId}")
    return workout_history
