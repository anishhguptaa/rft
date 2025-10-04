# models/goal.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DECIMAL,
    DateTime,
    Boolean,
    ForeignKey,
    func
)
from .user import Base  # Import the Base from your existing user model

class Goal(Base):
    """
    SQLAlchemy model for the 'goals' table.
    """
    __tablename__ = "goals"

    GoalId = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, ForeignKey("users.UserId"), nullable=False)
    GoalType = Column(String(50), nullable=False)
    TargetWeight = Column(DECIMAL(5, 2), nullable=True)
    TargetDate = Column(Date, nullable=True)
    Active = Column(Boolean, default=False)
    CreatedAt = Column(DateTime, server_default=func.now())
    UpdatedAt = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Goal(GoalId={self.GoalId}, UserId={self.UserId}, Type='{self.GoalType}')>"
