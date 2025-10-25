# models/goal.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    DECIMAL,
    DateTime,
    Boolean,
    ForeignKey,
    Enum,
    func
)
from .user import Base  # Import the Base from your existing user model
from models.Enums.enums import GoalType as GoalTypeEnum, WorkoutEquipment as WorkoutEquipmentEnum

class Goal(Base):
    """
    SQLAlchemy model for the 'goals' table.
    """
    __tablename__ = "goals"

    GoalId = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, ForeignKey("users.UserId"), nullable=False)
    GoalType = Column(Enum(GoalTypeEnum), nullable=False)
    NoOfWorkoutDaysInWeek = Column(Integer, nullable=True)
    TargetWeight = Column(DECIMAL(5, 2), nullable=True)
    initial_weight = Column(DECIMAL(5, 2), nullable=True)
    TargetDurationInWeeks = Column(Integer, nullable=True)
    WorkoutEquipment = Column(Enum(WorkoutEquipmentEnum), nullable=True)
    Remarks = Column(String(1000), nullable=True)
    Active = Column(Boolean, default=False)
    CreatedAt = Column(DateTime, server_default=func.now())
    UpdatedAt = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Goal(GoalId={self.GoalId}, UserId={self.UserId}, Type='{self.GoalType}')>"
