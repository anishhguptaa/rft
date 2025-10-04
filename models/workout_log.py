# models/workout_log.py
from sqlalchemy import (
    Column,
    Integer,
    DECIMAL,
    Boolean,
    ForeignKey,
    DateTime,
    func
)
from .user import Base  # Re-use the same Base

class WorkoutLog(Base):
    """
    SQLAlchemy model for the 'workout_logs' table.
    """
    __tablename__ = "workout_logs"

    WorkoutLogId = Column(Integer, primary_key=True, index=True)
    DailyWorkoutId = Column(Integer, ForeignKey("daily_workouts.DailyWorkoutId"), nullable=False)
    ExerciseId = Column(Integer, ForeignKey("exercises.ExerciseId"), nullable=False)
    Sets = Column(Integer)
    Reps = Column(Integer)
    WeightUsed = Column(DECIMAL(5, 2))
    DurationMin = Column(DECIMAL(5, 2), nullable=True)
    Completed = Column(Boolean, default=True)
    CreatedAt = Column(DateTime, server_default=func.now())
    UpdatedAt = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<WorkoutLog(WorkoutLogId={self.WorkoutLogId}, ExerciseId={self.ExerciseId})>"
