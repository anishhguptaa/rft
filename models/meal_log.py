# models/meal_log.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DECIMAL,
    ForeignKey,
    DateTime,
    func
)
from .user import Base  # Re-use the same Base

class MealLog(Base):
    """
    SQLAlchemy model for the 'meal_logs' table.
    """
    __tablename__ = "meal_logs"

    MealLogId = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, ForeignKey("users.UserId"), nullable=False)
    Date = Column(Date, nullable=False)
    MealType = Column(String(50))
    Description = Column(Text)
    Calories = Column(Integer)
    Protein = Column(DECIMAL(5, 2))
    Carbs = Column(DECIMAL(5, 2))
    Fats = Column(DECIMAL(5, 2))
    CreatedAt = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<MealLog(MealLogId={self.MealLogId}, UserId={self.UserId}, MealType='{self.MealType}')>"
