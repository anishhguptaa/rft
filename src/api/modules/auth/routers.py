"""
Authentication Routes
Handles authentication endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.db import get_db
from api.modules.auth.services import verify_user_credentials
from schemas.backend_schemas import LoginRequest, LoginResponse

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
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
