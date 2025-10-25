"""
User Services
Business logic for user operations
"""

from sqlalchemy.orm import Session
from models.DbModels.user import User
from models.DbModels.user_health_profile import UserHealthProfile
from models.DbModels.goal import Goal
from models.DbModels.daily_user_workout_routine_history import DailyUserWorkoutRoutineHistory
from datetime import date, timedelta


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    Retrieves a user from the database by their unique ID.

    Args:
        db: The SQLAlchemy database session.
        user_id: The ID of the user to retrieve.

    Returns:
        The User object if found, otherwise None.
    """
    return db.query(User).filter(User.UserId == user_id).first()


def update_user_basic_info(
    db: Session,
    user_id: int,
    *,
    name: str,
    age: int,
    gender: str,
    height_cm: float,
    weight_kg: float,
    user_experience_level,
) -> User:
    """Update basic user info with validation.

    Raises:
        ValueError: if any provided field is invalid.
        LookupError: if user does not exist.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise LookupError("User not found")

    # Name validation
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Name cannot be empty")

    # Age validation (reasonable human range)
    if not isinstance(age, int) or age < 1 or age > 120:
        raise ValueError("Please enter a valid age between 1 and 120")

    # Gender validation
    allowed_genders = {"MALE", "FEMALE"}
    gender_upper = str(gender).strip().upper()
    if gender_upper not in allowed_genders:
        raise ValueError("Gender must be MALE or FEMALE")

    # Height and weight validation with real-world bounds
    # Tallest verified ~272 cm, shortest viable adult ~54 cm
    if not (54.0 <= float(height_cm) <= 272.0):
        raise ValueError("Please enter a valid height (in cm)")

    # Heaviest recorded ~635 kg, practical minimum > 2 kg for adults
    if not (2.0 <= float(weight_kg) <= 635.0):
        raise ValueError("Please enter a valid weight (in kg)")

    # Persist
    user.FullName = name.strip()
    user.Age = age
    user.Gender = gender_upper
    user.HeightCm = float(height_cm)
    user.WeightKg = float(weight_kg)
    user.UserExperienceLevel = user_experience_level

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_health_profile_by_user_id(db: Session, user_id: int) -> UserHealthProfile | None:
    """Return existing UserHealthProfile for a user, if any."""
    return (
        db.query(UserHealthProfile)
        .filter(UserHealthProfile.UserId == user_id)
        .first()
    )


def upsert_health_profile(
    db: Session,
    user_id: int,
    *,
    is_smoker: bool,
    pre_existing_diseases: list[str] | None = None,
    current_medications: list[str] | None = None,
    health_issues: list[str] | None = None,
    physical_limitations: list[str] | None = None,
) -> UserHealthProfile:
    """Create or update a user's health profile.

    If the user does not exist, raises LookupError.
    If the profile exists, updates it; otherwise creates a new one.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise LookupError("User not found")

    profile = get_health_profile_by_user_id(db, user_id)

    # Normalize lists
    pre_existing_diseases = pre_existing_diseases or []
    current_medications = current_medications or []
    health_issues = health_issues or []
    physical_limitations = physical_limitations or []

    if profile is None:
        profile = UserHealthProfile(
            UserId=user_id,
            IsSmoker=bool(is_smoker),
            PreExistingDiseases=list(pre_existing_diseases),
            CurrentMedications=list(current_medications),
            HealthIssues=list(health_issues),
            PhysicalLimitations=list(physical_limitations),
        )
        db.add(profile)
    else:
        profile.IsSmoker = bool(is_smoker)
        profile.PreExistingDiseases = list(pre_existing_diseases)
        profile.CurrentMedications = list(current_medications)
        profile.HealthIssues = list(health_issues)
        profile.PhysicalLimitations = list(physical_limitations)

    db.commit()
    db.refresh(profile)
    return profile


def get_active_user_goal(db: Session, user_id: int) -> Goal | None:
    """Get the active goal for a user."""
    return (
        db.query(Goal)
        .filter(Goal.UserId == user_id, Goal.Active == True)
        .first()
    )


def set_user_goal(
    db: Session,
    user_id: int,
    *,
    goal_type,
    no_of_workout_days_in_week: int | None = None,
    target_weight: float | None = None,
    target_duration_in_weeks: int | None = None,
    workout_equipment = None,
    remarks: str | None = None,
) -> Goal:
    """Set a new goal for the user.
    
    If an active goal exists, soft delete it (set Active=False).
    Then create a new active goal.
    
    Raises:
        LookupError: if user does not exist.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise LookupError("User not found")
    
    # Soft delete any existing active goal
    existing_goal = get_active_user_goal(db, user_id)
    if existing_goal:
        existing_goal.Active = False
        db.add(existing_goal)
    
    # Create new active goal
    new_goal = Goal(
        UserId=user_id,
        GoalType=goal_type,
        NoOfWorkoutDaysInWeek=no_of_workout_days_in_week,
        TargetWeight=target_weight,
        initial_weight=user.CurrentWeight,
        TargetDurationInWeeks=target_duration_in_weeks,
        WorkoutEquipment=workout_equipment,
        Remarks=remarks,
        Active=True,
    )
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return new_goal


def get_user_stats(db: Session, user_id: int) -> dict:
    """
    Get user statistics including goal status, live streak, and yesterday's workout status.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Dictionary containing:
        - isGoalSet: bool - True if user has an active goal
        - liveStreak: int - Number of consecutive days user has worked out (including today)
        - YesterdayMissedWorkout: bool - True if user did NOT workout yesterday
    """
    
    # 1. Check if goal is set
    active_goal = get_active_user_goal(db, user_id)
    is_goal_set = active_goal is not None
    
    # 2. Calculate live streak (consecutive workout days including today)
    live_streak = 0
    current_date = date.today()
    
    # Check backwards from today to find consecutive workout days
    while True:
        workout = (
            db.query(DailyUserWorkoutRoutineHistory)
            .filter(
                DailyUserWorkoutRoutineHistory.UserId == user_id,
                DailyUserWorkoutRoutineHistory.Date == current_date,
                DailyUserWorkoutRoutineHistory.IsCompleted == True
            )
            .first()
        )
        
        if workout:
            live_streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    # 3. Check if user missed workout yesterday
    yesterday = date.today() - timedelta(days=1)
    yesterday_workout = (
        db.query(DailyUserWorkoutRoutineHistory)
        .filter(
            DailyUserWorkoutRoutineHistory.UserId == user_id,
            DailyUserWorkoutRoutineHistory.Date == yesterday,
            DailyUserWorkoutRoutineHistory.IsCompleted == True
        )
        .first()
    )
    
    yesterday_missed_workout = yesterday_workout is None
    
    return {
        "isGoalSet": is_goal_set,
        "liveStreak": live_streak,
        "YesterdayMissedWorkout": yesterday_missed_workout
    }
