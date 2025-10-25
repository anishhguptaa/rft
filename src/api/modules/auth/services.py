"""
Authentication Services
Business logic for JWT-based authentication operations
"""

from sqlalchemy.orm import Session
from models.DbModels.user import User
from models.DbModels.user_session import UserSession
from core.password_utils import hash_password, verify_password
from core.jwt_utils import create_access_token, create_refresh_token, verify_token, get_token_expiry
from core.logger import get_logger
from datetime import datetime
from typing import Optional, Dict, Any

logger = get_logger(__name__)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Retrieves a user from the database by their email address.

    Args:
        db: The SQLAlchemy database session.
        email: The email address of the user to retrieve.

    Returns:
        The User object if found, otherwise None.
    """
    return db.query(User).filter(User.Email == email).first()


def create_user(db: Session, email: str, password: str, full_name: str = "") -> User:
    """
    Create a new user with hashed password.
    
    Args:
        db: Database session
        email: User's email address
        password: Plain text password
        full_name: User's full name (optional, defaults to empty string)
        
    Returns:
        Created User object
        
    Raises:
        ValueError: If email already exists
    """
    logger.info(f"Creating new user with email: {email}")
    
    # Check if user already exists
    existing_user = get_user_by_email(db, email)
    if existing_user:
        logger.warning(f"User creation failed - email already exists: {email}")
        raise ValueError("Email already registered")
    
    # Hash the password
    password_hash = hash_password(password)
    logger.debug("Password hashed successfully")
    
    # Create new user
    new_user = User(
        Email=email,
        PasswordHash=password_hash,
        FullName=full_name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"User created successfully with ID: {new_user.UserId}")
    return new_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password.
    
    Args:
        db: Database session
        email: User's email address
        password: Plain text password
        
    Returns:
        User object if authentication successful, None otherwise
    """
    logger.debug(f"Authenticating user with email: {email}")
    
    user = get_user_by_email(db, email)
    
    if not user:
        logger.debug(f"Authentication failed - user not found: {email}")
        return None
    
    # Verify password using bcrypt
    if not verify_password(password, user.PasswordHash):
        logger.debug(f"Authentication failed - invalid password for email: {email}")
        return None
    
    logger.debug(f"Authentication successful for user ID: {user.UserId}")
    return user


def create_user_session(db: Session, user_id: int, refresh_token: str) -> UserSession:
    """
    Create a new user session with refresh token.
    
    Args:
        db: Database session
        user_id: User ID
        refresh_token: JWT refresh token
        
    Returns:
        Created UserSession object
    """
    logger.debug(f"Creating session for user ID: {user_id}")
    
    expires_at = get_token_expiry("refresh")
    
    session = UserSession(
        UserId=user_id,
        RefreshToken=refresh_token,
        ExpiresAt=expires_at,
        IsValid=True
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    logger.debug(f"Session created successfully with ID: {session.SessionId}")
    return session


def get_session_by_refresh_token(db: Session, refresh_token: str) -> Optional[UserSession]:
    """
    Get a user session by refresh token.
    
    Args:
        db: Database session
        refresh_token: JWT refresh token
        
    Returns:
        UserSession object if found and valid, None otherwise
    """
    session = db.query(UserSession).filter(
        UserSession.RefreshToken == refresh_token,
        UserSession.IsValid == True,
        UserSession.ExpiresAt > datetime.utcnow()
    ).first()
    
    return session


def invalidate_session(db: Session, refresh_token: str) -> bool:
    """
    Invalidate a user session (logout).
    
    Args:
        db: Database session
        refresh_token: JWT refresh token
        
    Returns:
        True if session was invalidated, False if not found
    """
    logger.debug("Invalidating user session")
    
    session = db.query(UserSession).filter(
        UserSession.RefreshToken == refresh_token
    ).first()
    
    if not session:
        logger.warning("Session not found for invalidation")
        return False
    
    session.IsValid = False
    db.commit()
    
    logger.debug(f"Session invalidated successfully for user ID: {session.UserId}")
    return True


def invalidate_all_user_sessions(db: Session, user_id: int) -> int:
    """
    Invalidate all sessions for a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Number of sessions invalidated
    """
    count = db.query(UserSession).filter(
        UserSession.UserId == user_id,
        UserSession.IsValid == True
    ).update({"IsValid": False})
    
    db.commit()
    
    return count


def generate_tokens(user: User) -> Dict[str, str]:
    """
    Generate access and refresh tokens for a user.
    
    Args:
        user: User object
        
    Returns:
        Dictionary containing access_token and refresh_token
    """
    token_data = {
        "user_id": user.UserId,
        "email": user.Email
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

