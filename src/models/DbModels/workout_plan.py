# models/workout_plan.py
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
from .user import Base # Re-use the same Base

class WorkoutPlan(Base):
    """
    SQLAlchemy model for the 'workout_plans' table.
    """
    __tablename__ = "workout_plans"

    PlanId = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, ForeignKey("users.UserId"), nullable=False)
    PlanName = Column(String(100), nullable=False)
    GeneratedByAI = Column(Boolean, default=False)
    StartDate = Column(Date, nullable=True)
    EndDate = Column(Date, nullable=True)
    IsActive = Column(Boolean, default=True)
    PlanVersion = Column(Integer, default=1)
    CreatedAt = Column(DateTime, server_default=func.now())
    UpdatedAt = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<WorkoutPlan(PlanId={self.PlanId}, Name='{self.PlanName}', UserId={self.UserId})>"
