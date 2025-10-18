"""
Application Enums
Centralized location for all enum definitions used across the application
"""

from enum import Enum


class UserEquipment(str, Enum):
    """
    Enum for user equipment availability
    """
    NO_EQUIPMENT = "NoEquipment"
    DUMBBELLS_ONLY = "DumbbellsOnly"
    FULL_GYM_EQUIPMENT = "FullGymEquipment"


class GoalType(str, Enum):
    """
    Enum for user fitness goal types
    """
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    MUSCLE_GAIN = "muscle_gain"
    ENDURANCE = "endurance"
    STRENGTH = "strength"


class WorkoutEquipment(str, Enum):
    """
    Enum for workout equipment availability
    """
    GYM = "gym"
    HOME_BODYWEIGHT = "home_bodyweight"
    HOME_DUMBBELLS = "home_dumbbells"


class UserExperienceLevel(str, Enum):
    """
    Enum for user experience level
    """
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class DayOfWeek(str, Enum):
    """
    Enum for days of the week
    """
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class ScheduleStatus(str, Enum):
    """
    Enum for weekly schedule status
    """
    PENDING = "pending"
    STARTED = "started"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    SWAPPED = "swapped"
