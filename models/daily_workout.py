# models/daily_workout.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Boolean,
    ForeignKey,
    DateTime,
    func
)
from .user import Base  # Re-use the same Base

class DailyWorkout(Base):
    """
    SQLAlchemy model for the 'daily_workouts' table.
    """
    __tablename__ = "daily_workouts"

    DailyWorkoutId = Column(Integer, primary_key=True, index=True)
    PlanId = Column(Integer, ForeignKey("workout_plans.PlanId"), nullable=False)
    Date = Column(Date, nullable=False)
    WorkoutFocus = Column(String(100))
    IsCompleted = Column(Boolean, default=False)
    Missed = Column(Boolean, default=False)
    AIAdjusted = Column(Boolean, default=False)
    CreatedAt = Column(DateTime, server_default=func.now())
    UpdatedAt = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<DailyWorkout(DailyWorkoutId={self.DailyWorkoutId}, Date='{self.Date}', PlanId={self.PlanId})>"
