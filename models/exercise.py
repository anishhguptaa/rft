# models/exercise.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    func
)
from .user import Base  # Re-use the same Base

class Exercise(Base):
    """
    SQLAlchemy model for the 'exercises' table.
    """
    __tablename__ = "exercises"

    ExerciseId = Column(Integer, primary_key=True, index=True)
    Name = Column(String(100), nullable=False, index=True)
    MuscleGroup = Column(String(50))
    Equipment = Column(String(50))
    Difficulty = Column(String(20))
    Instructions = Column(Text, nullable=True)
    VideoUrl = Column(String(255), nullable=True)
    CreatedAt = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Exercise(ExerciseId={self.ExerciseId}, Name='{self.Name}')>"
