# models/workout_plan.py
from sqlalchemy import (
    BigInteger,
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

    PlanId = Column(BigInteger, primary_key=True, index=True) #
    UserId = Column(BigInteger, ForeignKey("users.UserId"), nullable=False) #
    GeneratedByAI = Column(Boolean, default=False)
    StartDate = Column(Date, nullable=True)
    EndDate = Column(Date, nullable=True)
    IsActive = Column(Boolean, default=True)
    PlanVersion = Column(Integer, default=1)
    Overview = Column(String(10000), nullable=False)
    MealJson = Column(String, nullable=True)
    CreatedAt = Column(DateTime, server_default=func.now())
    Weekly_Plan_Summary = Column(String, nullable=True)
    

    def __repr__(self):
        return f"<WorkoutPlan(PlanId={self.PlanId}, Name='{self.PlanName}', UserId={self.UserId})>"
