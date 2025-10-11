"""
User Routes
Handles user management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.db import get_db
from api.modules.user.services import get_user_by_id
from schemas.backend_schemas import UserResponse

router = APIRouter()


@router.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single user by their ID.

    Args:
        user_id: The integer ID of the user to retrieve.
        db: Database session dependency
        
    Returns:
        UserResponse with user details
    """
    db_user = get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
