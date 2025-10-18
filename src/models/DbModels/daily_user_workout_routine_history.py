# models/daily_workout.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Boolean,
    ForeignKey,
    DateTime,
    Float,
    func
)
from .user import Base  # Re-use the same Base

class DailyUserWorkoutRoutineHistory(Base):
    """
    SQLAlchemy model for the 'UserWorkoutRoutineHistory' table.
    """
    __tablename__ = "daily_user_workout_routine_history"

    UserWorkoutRoutineHistoryId = Column(Integer, primary_key=True, index=True)
    PlanId = Column(Integer, ForeignKey("workout_plans.PlanId"), nullable=False)
    RoutineId = Column(Integer, ForeignKey("routines.RoutineId"), nullable=False)
    ScheduleId = Column(Integer, ForeignKey("weekly_schedule.ScheduleId"), nullable=False)
    UserId = Column(Integer, ForeignKey("users.UserId"), nullable=False)
    Date = Column(Date, nullable=False)
    IsCompleted = Column(Boolean, default=False)
    TodayWeight = Column(Float, nullable=True)
    WorkoutNotes = Column(String(255), nullable=True)
    CreatedAt = Column(DateTime, server_default=func.now())
    UpdatedAt = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<UserWorkoutRoutineHistory(UserWorkoutRoutineHistoryId={self.UserWorkoutRoutineHistoryId}, Date='{self.Date}', PlanId={self.PlanId})>"
