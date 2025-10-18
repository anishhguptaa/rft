from sqlalchemy import (
    BigInteger,
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    Enum,
    func
)
from .user import Base  # Reuse same Base
from models.Enums.enums import DayOfWeek, ScheduleStatus

class WeeklySchedule(Base):
    """
    SQLAlchemy model for the 'weekly_schedule' table.
    Represents the daily mapping of a user's weekly workout plan,
    including assigned routines, completion status, and rest days.
    """
    __tablename__ = "weekly_schedule"

    ScheduleId = Column(Integer, primary_key=True, index=True, autoincrement=True)
    PlanId = Column(BigInteger, ForeignKey("workout_plans.PlanId"), nullable=False)
    DayOfWeek = Column(Enum(DayOfWeek), nullable=False)
    RoutineId = Column(BigInteger, ForeignKey("routines.RoutineId"), nullable=True)
    Status = Column(Enum(ScheduleStatus), nullable=False, default=ScheduleStatus.PENDING)
    CompletedAt = Column(DateTime(timezone=True), nullable=True)
    UserFeedback = Column(Text, nullable=True)
    IsRestDay = Column(Boolean, default=False)
    CreatedAt = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return (
            f"<WeeklySchedule(ScheduleId={self.ScheduleId}, "
            f"PlanId={self.PlanId}, Day='{self.DayOfWeek}', "
            f"Status='{self.Status}', IsRestDay={self.IsRestDay})>"
        )