"""
User Routes
Handles user management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.db import get_db
from api.modules.user.services import (
    get_user_by_id,
    update_user_basic_info,
    upsert_health_profile,
    get_health_profile_by_user_id,
    get_active_user_goal,
    set_user_goal,
)
from schemas.backend_schemas import (
    UserResponse,
    UpdateUserBasicInfoRequest,
    UserHealthProfileRequest,
    UserHealthProfileResponse,
    SetUserGoalRequest,
    UserGoalResponse,
)

router = APIRouter()


@router.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single user by their ID with additional stats.

    Args:
        user_id: The integer ID of the user to retrieve.
        db: Database session dependency
        
    Returns:
        UserResponse with user details including:
        - isGoalSet: Whether user has an active goal
        - liveStreak: Number of consecutive workout days
        - YesterdayMissedWorkout: Whether user missed workout yesterday
    """
    from api.modules.user.services import get_user_stats
    
    db_user = get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user stats
    user_stats = get_user_stats(db, user_id)
    
    # Convert user object to dict and merge with stats
    user_dict = {
        "UserId": db_user.UserId,
        "FullName": db_user.FullName,
        "Email": db_user.Email,
        "Gender": db_user.Gender,
        "Age": db_user.Age,
        "HeightCm": db_user.HeightCm,
        "WeightKg": db_user.WeightKg,
        "UserExperienceLevel": db_user.UserExperienceLevel.value if db_user.UserExperienceLevel else None,
        **user_stats  # Merge stats (isGoalSet, liveStreak, YesterdayMissedWorkout)
    }
    
    return user_dict


@router.post("/users/{user_id}/basic-info", response_model=UserResponse)
def update_basic_info(
    user_id: int,
    payload: UpdateUserBasicInfoRequest,
    db: Session = Depends(get_db),
):
    """Update a user's basic information.

    Assumes the user row already exists. If not found, raises 404.
    Validates gender, height, weight, age and name with sensible bounds.
    """
    try:
        updated = update_user_basic_info(
            db,
            user_id,
            name=payload.name,
            age=payload.Age,
            gender=payload.Gender,
            height_cm=payload.height,
            weight_kg=payload.weight,
            user_experience_level=payload.UserExperienceLevel,
        )
        return updated
    except LookupError:
        raise HTTPException(status_code=404, detail="User not found")
    except ValueError as e:
        # Map validation errors to friendly messages as requested
        msg = str(e)
        if "weight" in msg.lower():
            msg = "Please enter a valid weight"
        elif "height" in msg.lower():
            msg = "Please enter a valid height"
        elif "gender" in msg.lower():
            msg = "Gender must be MALE or FEMALE"
        raise HTTPException(status_code=400, detail=msg)


@router.post("/users/{user_id}/health-profile", response_model=UserHealthProfileResponse)
def upsert_user_health_profile(
    user_id: int,
    payload: UserHealthProfileRequest,
    db: Session = Depends(get_db),
):
    """Create or update the user's health profile.

    If a health profile exists, update it; otherwise create a new one.
    Returns the saved profile.
    """
    try:
        profile = upsert_health_profile(
            db,
            user_id,
            is_smoker=payload.IsSmoker,
            pre_existing_diseases=payload.PreExistingDiseases,
            current_medications=payload.CurrentMedications,
            health_issues=payload.HealthIssues,
            physical_limitations=payload.PhysicalLimitations,
        )
        return profile
    except LookupError:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/users/{user_id}/health-profile", response_model=UserHealthProfileResponse)
def get_user_health_profile(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Get the user's health profile data.

    Returns the health profile if it exists.
    Checks if user exists first.
    """
    # Check if user exists
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get health profile
    profile = get_health_profile_by_user_id(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Health profile not found")
    
    return profile


@router.post("/users/{user_id}/goal", response_model=UserGoalResponse)
def set_user_goal_endpoint(
    user_id: int,
    payload: SetUserGoalRequest,
    db: Session = Depends(get_db),
):
    """Set a new goal for the user.
    
    If an active goal exists, it will be soft deleted (Active=False)
    and a new active goal will be created.
    Only one goal can be active at a time.
    """
    try:
        goal = set_user_goal(
            db,
            user_id,
            goal_type=payload.GoalType,
            no_of_workout_days_in_week=payload.NoOfWorkoutDaysInWeek,
            target_weight=payload.TargetWeight,
            target_duration_in_weeks=payload.TargetDurationInWeeks,
            workout_equipment=payload.WorkoutEquipment,
            remarks=payload.Remarks,
        )
        return goal
    except LookupError:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/users/{user_id}/goal", response_model=UserGoalResponse)
def get_user_goal_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Get the active goal for a user.
    
    Returns the currently active goal if one exists.
    """
    # Check if user exists
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get active goal
    goal = get_active_user_goal(db, user_id)
    if not goal:
        raise HTTPException(status_code=404, detail="No active goal found")
    
    return goal
