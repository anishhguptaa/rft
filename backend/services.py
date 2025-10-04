"""
Backend Services
Business logic for backend operations
"""

from sqlalchemy.orm import Session
from models.user import User
import hashlib

def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    Retrieves a user from the database by their unique ID.

    Args:
        db: The SQLAlchemy database session.
        user_id: The ID of the user to retrieve.

    Returns:
        The User object if found, otherwise None.
    """
    return db.query(User).filter(User.UserId == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Retrieves a user from the database by their email address.

    Args:
        db: The SQLAlchemy database session.
        email: The email address of the user to retrieve.

    Returns:
        The User object if found, otherwise None.
    """
    return db.query(User).filter(User.Email == email).first()


def hash_password(password: str) -> str:
    """
    Hashes a password using SHA-256.

    Args:
        password: The plain text password to hash.

    Returns:
        The hashed password as a hexadecimal string.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_user_credentials(db: Session, email: str, password: str) -> tuple[bool, User | None]:
    """
    Verifies user credentials by checking email and password.

    Args:
        db: The SQLAlchemy database session.
        email: The user's email address.
        password: The plain text password to verify.

    Returns:
        A tuple containing (is_valid, user_object).
        - is_valid: True if credentials are valid, False otherwise.
        - user_object: The User object if valid, None otherwise.
    """
    # Get user by email
    user = get_user_by_email(db, email)
    
    if user is None:
        return False, None
    
    # Hash the provided password and compare with stored hash
    password_hash = hash_password(password)
    
    if password_hash == user.PasswordHash:
        return True, user
    else:
        return False, None