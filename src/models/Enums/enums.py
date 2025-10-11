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
