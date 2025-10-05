"""
Backend Schemas
Pydantic models for backend endpoints
"""
from pydantic import BaseModel, EmailStr
from typing import Optional

# Schema for returning user data.
# This ensures the password hash is NEVER sent to the client.
class UserResponse(BaseModel):
    UserId: int
    FullName: str
    Email: EmailStr
    Gender: Optional[str] = None
    Age: Optional[int] = None
    HeightCm: Optional[float] = None # Pydantic will handle the Decimal conversion
    WeightKg: Optional[float] = None

    class Config:
        from_attributes = True # Replaces orm_mode in Pydantic v2


# Schema for login request
class LoginRequest(BaseModel):
    emailId: EmailStr
    password: str


# Schema for login response
class LoginResponse(BaseModel):
    success: bool
    message: str
    userId: Optional[int] = None