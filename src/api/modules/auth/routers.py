"""
Authentication Routes
Handles JWT-based authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.datastructures import SameSite
from sqlalchemy.orm import Session

from core.db import get_db
from core.jwt_utils import verify_token
from core.config import settings
from core.logger import get_logger
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

logger = get_logger(__name__)

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
    logger.info(f"Signup attempt for email: {request.email}")
    try:
        # Create new user
        user = create_user(
            db=db,
            email=request.email,
            password=request.password
        )
        logger.info(f"User created successfully with ID: {user.UserId}")
        
        # Generate tokens
        tokens = generate_tokens(user)
        
        # Store refresh token in session
        create_user_session(
            db=db,
            user_id=user.UserId,
            refresh_token=tokens["refresh_token"]
        )
        logger.info(f"User session created for user ID: {user.UserId}")
        
        # Set access token as httpOnly cookie (expires in 15 minutes)
        response.set_cookie(
            key="access_token",
            value=tokens["access_token"],
            httponly=True,
            secure=not settings.DEBUG,  # Only send over HTTPS in production
            samesite=SameSite.LAX,  # CSRF protection
            max_age=900,  # 15 minutes in seconds
        )
        
        # Set refresh token as httpOnly cookie (expires in 7 days)
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=not settings.DEBUG,  # Only send over HTTPS in production
            samesite=SameSite.LAX,
            max_age=604800,  # 7 days in seconds
        )
        
        logger.info(f"Signup successful for user ID: {user.UserId}")
        return AuthResponse(
            success=True,
            message="User registered successfully",
            access_token=None,  # Don't send tokens in response body
            refresh_token=None,
            user_id=user.UserId
        )
    except ValueError as e:
        logger.warning(f"Signup failed - email already exists: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Signup failed with unexpected error for email {request.email}: {str(e)}")
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
    logger.info(f"Login attempt for email: {request.email}")
    
    # Authenticate user
    user = authenticate_user(db, request.email, request.password)
    
    if not user:
        logger.warning(f"Login failed - invalid credentials for email: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    logger.info(f"User authenticated successfully with ID: {user.UserId}")
    
    # Generate tokens
    tokens = generate_tokens(user)
    
    # Store refresh token in session
    create_user_session(
        db=db,
        user_id=user.UserId,
        refresh_token=tokens["refresh_token"]
    )
    logger.info(f"User session created for user ID: {user.UserId}")
    
    # Set access token as httpOnly cookie (expires in 15 minutes)
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=not settings.DEBUG,  # Only send over HTTPS in production
        samesite=SameSite.LAX,
        max_age=900,  # 15 minutes in seconds
    )
    
    # Set refresh token as httpOnly cookie (expires in 7 days)
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=not settings.DEBUG,  # Only send over HTTPS in production
        samesite=SameSite.LAX,
        max_age=604800,  # 7 days in seconds
    )
    
    logger.info(f"Login successful for user ID: {user.UserId}")
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
    logger.info("Token refresh attempt")
    
    # Get refresh token from cookie
    refresh_token_value = request.cookies.get("refresh_token")
    
    if not refresh_token_value:
        logger.warning("Token refresh failed - no refresh token in cookies")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found in cookies"
        )
    
    # Verify refresh token
    payload = verify_token(refresh_token_value, token_type="refresh")
    
    if not payload:
        logger.warning("Token refresh failed - invalid or expired refresh token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Check if session exists and is valid
    session = get_session_by_refresh_token(db, refresh_token_value)
    
    if not session:
        logger.warning("Token refresh failed - invalid or expired session")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    # Get user
    user = get_user_by_email(db, payload.get("email"))
    
    if not user:
        logger.warning(f"Token refresh failed - user not found for email: {payload.get('email')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    logger.info(f"Token refresh successful for user ID: {user.UserId}")
    
    # Generate new tokens
    tokens = generate_tokens(user)
    
    # Invalidate old session and create new one
    invalidate_session(db, refresh_token_value)
    create_user_session(
        db=db,
        user_id=user.UserId,
        refresh_token=tokens["refresh_token"]
    )
    logger.info(f"New session created for user ID: {user.UserId}")
    
    # Set new access token as httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=not settings.DEBUG,  # Only send over HTTPS in production
        samesite=SameSite.LAX,
        max_age=900,  # 15 minutes in seconds
    )
    
    # Set new refresh token as httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=not settings.DEBUG,  # Only send over HTTPS in production
        samesite=SameSite.LAX,
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
    logger.info("Logout attempt")
    
    # Get refresh token from cookie
    refresh_token_value = request.cookies.get("refresh_token")
    
    if refresh_token_value:
        # Invalidate the session
        invalidated = invalidate_session(db, refresh_token_value)
        if invalidated:
            logger.info("User session invalidated successfully")
        else:
            logger.warning("Failed to invalidate user session")
    else:
        logger.info("No refresh token found in cookies")
    
    # Clear both cookies
    response.delete_cookie(key="access_token", samesite=SameSite.LAX)
    response.delete_cookie(key="refresh_token", samesite=SameSite.LAX)
    
    logger.info("Logout completed successfully")
    return LogoutResponse(
        success=True,
        message="Logged out successfully"
    )
