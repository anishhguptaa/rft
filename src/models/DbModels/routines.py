from sqlalchemy import (
    BigInteger,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    func
)
from .user import Base  # Re-use the same Base

class Routines(Base):
    """
    SQLAlchemy model for the 'Routines' table.
    Represents a weekly or daily workout routine linked to a workout plan.
    """
    __tablename__ = "routines"

    RoutineId = Column(BigInteger, primary_key=True, index=True)
    PlanId = Column(BigInteger, ForeignKey("workout_plans.PlanId"), nullable=False)
    RoutineName = Column(String(100), nullable=False)
    Focus = Column(String(100), nullable=True)  # e.g., "Leg Day", "Push Day", "Full Body"
    RoutineJson = Column(String, nullable=True)  # Store JSON as string (or change to JSON if supported)
    CreatedAt = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Routine(RoutineId={self.RoutineId}, PlanId={self.PlanId}, Name='{self.RoutineName}')>"