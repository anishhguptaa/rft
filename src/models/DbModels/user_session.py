"""
User Session Model
Stores refresh tokens and session information
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from .user import Base


class UserSession(Base):
    """
    SQLAlchemy model for the 'user_sessions' table.
    Stores refresh tokens for JWT authentication.
    """
    __tablename__ = "user_sessions"

    SessionId = Column(Integer, primary_key=True, autoincrement=True, index=True)
    UserId = Column(Integer, ForeignKey("users.UserId"), nullable=False)
    RefreshToken = Column(String(500), nullable=False, unique=True)
    ExpiresAt = Column(DateTime, nullable=False)
    IsValid = Column(Boolean, default=True, nullable=False)
    CreatedAt = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<UserSession(SessionId={self.SessionId}, UserId={self.UserId}, IsValid={self.IsValid})>"
