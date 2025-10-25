# models/user_health_profile.py
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, JSON, String
from sqlalchemy.sql import func
from models.DbModels.user import Base

class UserHealthProfile(Base):
    __tablename__ = "user_health_profiles"

    Id = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, ForeignKey("users.UserId", ondelete="CASCADE"))
    IsSmoker = Column(Boolean, default=False)

    # Existing health fields
    PreExistingDiseases = Column(JSON, nullable=True)
    CurrentMedications = Column(JSON, nullable=True)
    HealthIssues = Column(JSON, nullable=True)
    PhysicalLimitations = Column(JSON, nullable=True)
    
    # Meal plan related fields
    Allergies = Column(JSON, nullable=True)  # List of allergies (e.g., ["peanut", "shellfish"])
    Intolerances = Column(JSON, nullable=True)  # List of intolerances (e.g., ["lactose", "gluten"])
    DietType = Column(String(50), nullable=True)  # Diet type: "veg", "non_veg", "vegan"
    DislikedFoods = Column(JSON, nullable=True)  # List of disliked foods
    LocationCountry = Column(String(100), nullable=True)  # Country for ingredient availability
    MealPlanRemarks = Column(String(1000), nullable=True)  # Additional meal plan remarks

    CreatedAt = Column(DateTime(timezone=True), server_default=func.now())
    UpdatedAt = Column(DateTime(timezone=True), onupdate=func.now())