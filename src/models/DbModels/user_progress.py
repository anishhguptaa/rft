# models/user_progress.py
from sqlalchemy import (
    Column,
    Integer,
    Date,
    Text,
    ForeignKey,
    DateTime,
    func
)
from .user import Base  # Re-use the same Base

class UserProgress(Base):
    """
    SQLAlchemy model for the 'user_progress' table.
    """
    __tablename__ = "user_progress"

    ProgressId = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, ForeignKey("users.UserId"), nullable=False)
    WeekStart = Column(Date, nullable=False)
    WorkoutsCompleted = Column(Integer, default=0)
    WorkoutsMissed = Column(Integer, default=0)
    TotalCaloriesBurned = Column(Integer, default=0)
    StreakDays = Column(Integer, default=0)
    AIComment = Column(Text, nullable=True)
    CreatedAt = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<UserProgress(ProgressId={self.ProgressId}, UserId={self.UserId}, WeekStart='{self.WeekStart}')>"
