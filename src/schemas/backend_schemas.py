"""
Backend Schemas
Pydantic models for backend endpoints
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union
from models.Enums.enums import GoalType, WorkoutEquipment, UserExperienceLevel

# Schema for returning user data.
# This ensures the password hash is NEVER sent to the client.
class UserResponse(BaseModel):
    UserId: int
    FullName: str
    Email: EmailStr
    Gender: Optional[str] = None
    Age: Optional[int] = None
    HeightCm: Optional[float] = None # Pydantic will handle the Decimal conversion
    WeightKg: Optional[float] = None
    UserExperienceLevel: Optional[str] = None
    isGoalSet: Optional[bool] = None
    liveStreak: Optional[int] = None
    YesterdayMissedWorkout: Optional[bool] = None

    class Config:
        from_attributes = True # Replaces orm_mode in Pydantic v2


# Schema for login request
class LoginRequest(BaseModel):
    emailId: EmailStr
    password: str


# Schema for login response
class LoginResponse(BaseModel):
    success: bool
    message: str
    userId: Optional[int] = None


# Request schema to update user's basic info
class UpdateUserBasicInfoRequest(BaseModel):
    name: str
    Age: int
    Gender: str
    height: float
    weight: float
    UserExperienceLevel: UserExperienceLevel


# Request schema for user health profile upsert
class UserHealthProfileRequest(BaseModel):
    IsSmoker: bool
    PreExistingDiseases: List[str] = []
    CurrentMedications: List[str] = []
    HealthIssues: List[str] = []
    PhysicalLimitations: List[str] = []


# Response schema for user health profile
class UserHealthProfileResponse(BaseModel):
    Id: int
    UserId: int
    IsSmoker: bool
    PreExistingDiseases: List[str] = []
    CurrentMedications: List[str] = []
    HealthIssues: List[str] = []
    PhysicalLimitations: List[str] = []

    class Config:
        from_attributes = True


# Request schema for setting user goal
class SetUserGoalRequest(BaseModel):
    GoalType: GoalType
    NoOfWorkoutDaysInWeek: Optional[int] = None
    TargetWeight: Optional[float] = None
    TargetDurationInWeeks: Optional[int] = None
    WorkoutEquipment: WorkoutEquipment
    Remarks: Optional[str] = None


# Response schema for user goal
class UserGoalResponse(BaseModel):
    GoalId: int
    UserId: int
    GoalType: str  # Change to string to avoid enum issues
    NoOfWorkoutDaysInWeek: Optional[int] = None
    TargetWeight: Optional[float] = None
    TargetDurationInWeeks: Optional[int] = None
    WorkoutEquipment: Optional[str] = None  # Change to string to avoid enum issues
    Remarks: Optional[str] = None
    Active: bool

    class Config:
        from_attributes = True