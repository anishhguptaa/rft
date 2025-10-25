"""
Authentication Routes
Handles JWT-based authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session

from core.db import get_db
from core.jwt_utils import verify_token
from api.modules.auth.services import (
    create_user,
    authenticate_user,
    generate_tokens,
    create_user_session,
    get_session_by_refresh_token,
    invalidate_session,
    get_user_by_email
)
from schemas.backend_schemas import (
    SignupRequest,
    LoginRequest,
    AuthResponse,
    RefreshTokenRequest,
    LogoutRequest,
    LogoutResponse
)

router = APIRouter()


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest, response: Response, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Creates a new user account with hashed password and sets JWT tokens as httpOnly cookies.
    
    Args:
        request: SignupRequest containing email and password
        response: Response object to set cookies
        db: Database session
        
    Returns:
        AuthResponse with success status and user_id
        
    Raises:
        400: If email already exists
    """
    try:
        # Create new user
        user = create_user(
            db=db,
            email=request.email,
            password=request.password
        )
        
        # Generate tokens
        tokens = generate_tokens(user)
        
        # Store refresh token in session
        create_user_session(
            db=db,
            user_id=user.UserId,
            refresh_token=tokens["refresh_token"]
        )
        
        # Set access token as httpOnly cookie (expires in 15 minutes)
        response.set_cookie(
            key="access_token",
            value=tokens["access_token"],
            httponly=True,
            secure=True,  # Only send over HTTPS in production
            samesite="lax",  # CSRF protection
            max_age=900,  # 15 minutes in seconds
        )
        
        # Set refresh token as httpOnly cookie (expires in 7 days)
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=604800,  # 7 days in seconds
        )
        
        return AuthResponse(
            success=True,
            message="User registered successfully",
            access_token=None,  # Don't send tokens in response body
            refresh_token=None,
            user_id=user.UserId
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """
    Login a user.
    
    Authenticates user credentials and sets JWT tokens as httpOnly cookies.
    
    Args:
        request: LoginRequest containing email and password
        response: Response object to set cookies
        db: Database session
        
    Returns:
        AuthResponse with success status and user_id
        
    Raises:
        401: If credentials are invalid
    """
    # Authenticate user
    user = authenticate_user(db, request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate tokens
    tokens = generate_tokens(user)
    
    # Store refresh token in session
    create_user_session(
        db=db,
        user_id=user.UserId,
        refresh_token=tokens["refresh_token"]
    )
    
    # Set access token as httpOnly cookie (expires in 15 minutes)
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=900,  # 15 minutes in seconds
    )
    
    # Set refresh token as httpOnly cookie (expires in 7 days)
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=604800,  # 7 days in seconds
    )
    
    return AuthResponse(
        success=True,
        message="Login successful",
        access_token=None,  # Don't send tokens in response body
        refresh_token=None,
        user_id=user.UserId
    )


@router.post("/refresh", response_model=AuthResponse)
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token from cookie.
    
    Validates the refresh token and generates new tokens, setting them as httpOnly cookies.
    
    Args:
        request: Request object to read cookies
        response: Response object to set cookies
        db: Database session
        
    Returns:
        AuthResponse with success status
        
    Raises:
        401: If refresh token is invalid or expired
    """
    # Get refresh token from cookie
    refresh_token_value = request.cookies.get("refresh_token")
    
    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found in cookies"
        )
    
    # Verify refresh token
    payload = verify_token(refresh_token_value, token_type="refresh")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Check if session exists and is valid
    session = get_session_by_refresh_token(db, refresh_token_value)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    # Get user
    user = get_user_by_email(db, payload.get("email"))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Generate new tokens
    tokens = generate_tokens(user)
    
    # Invalidate old session and create new one
    invalidate_session(db, refresh_token_value)
    create_user_session(
        db=db,
        user_id=user.UserId,
        refresh_token=tokens["refresh_token"]
    )
    
    # Set new access token as httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=900,  # 15 minutes in seconds
    )
    
    # Set new refresh token as httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=604800,  # 7 days in seconds
    )
    
    return AuthResponse(
        success=True,
        message="Token refreshed successfully",
        access_token=None,  # Don't send tokens in response body
        refresh_token=None,
        user_id=user.UserId
    )


@router.post("/logout", response_model=LogoutResponse)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Logout a user.
    
    Invalidates the refresh token from cookie and clears both cookies.
    
    Args:
        request: Request object to read cookies
        response: Response object to clear cookies
        db: Database session
        
    Returns:
        LogoutResponse with success status
    """
    # Get refresh token from cookie
    refresh_token_value = request.cookies.get("refresh_token")
    
    if refresh_token_value:
        # Invalidate the session
        invalidate_session(db, refresh_token_value)
    
    # Clear both cookies
    response.delete_cookie(key="access_token", samesite="lax")
    response.delete_cookie(key="refresh_token", samesite="lax")
    
    return LogoutResponse(
        success=True,
        message="Logged out successfully"
    )
