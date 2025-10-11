"""
User Services
Business logic for user operations
"""

from sqlalchemy.orm import Session
from models.DbModels.user import User


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
