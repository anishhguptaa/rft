# models/user.py
from sqlalchemy import (
    Column,
    Integer,
    Nullable,
    String,
    DECIMAL,
    DateTime,
    func
)
from sqlalchemy.orm import declarative_base

# The DeclarativeBase is a factory for creating base classes for your models.
# All your models will inherit from this.
Base = declarative_base()

class User(Base):
    """
    SQLAlchemy model for the 'users' table.
    """
    __tablename__ = "users"

    UserId = Column(Integer, primary_key=True, index=True)
    FullName = Column(String(100), nullable=False)
    Email = Column(String(150), unique=True, index=True, nullable=False)
    PasswordHash = Column(String(255), nullable=False)
    Gender = Column(String(10))
    Age = Column(Integer, nullable=False)
    HeightCm = Column(DECIMAL(5, 2))
    WeightKg = Column(DECIMAL(5, 2))
    UserEquipment = Column(String(255))
    CreatedAt = Column(DateTime, server_default=func.now())
    UpdatedAt = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User(UserId={self.UserId}, Email='{self.Email}')>"
