# models/user_health_profile.py
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from models.DbModels.user import Base

class UserHealthProfile(Base):
    __tablename__ = "user_health_profiles"

    Id = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, ForeignKey("users.UserId", ondelete="CASCADE"))
    IsSmoker = Column(Boolean, default=False)

    PreExistingDiseases = Column(JSON, nullable=True)
    CurrentMedications = Column(JSON, nullable=True)
    HealthIssues = Column(JSON, nullable=True)
    PhysicalLimitations = Column(JSON, nullable=True)

    CreatedAt = Column(DateTime(timezone=True), server_default=func.now())
    UpdatedAt = Column(DateTime(timezone=True), onupdate=func.now())