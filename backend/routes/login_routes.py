"""
Login Routes
Handles authentication endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.db import get_db
from backend.services import verify_user_credentials
from schemas.backend_schemas import LoginRequest, LoginResponse

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login API endpoint that authenticates a user.
    
    Takes emailId and password, retrieves the user from the database,
    hashes the password, and verifies if the credentials are valid.
    
    Args:
        request: LoginRequest containing emailId and password
        db: Database session dependency
        
    Returns:
        LoginResponse with success status, message, and userId if successful
    """
    # Verify user credentials
    is_valid, user = verify_user_credentials(db, request.emailId, request.password)
    
    if is_valid and user:
        return LoginResponse(
            success=True,
            message="Login successful",
            userId=user.UserId
        )
    else:
        return LoginResponse(
            success=False,
            message="Invalid email or password",
            userId=None
        )
