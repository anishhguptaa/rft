"""
Authentication Middleware
Verifies JWT access tokens and attaches user to request state
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.jwt_utils import verify_token
from typing import Optional

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = security
) -> dict:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Extracts the JWT token from the Authorization header, verifies it,
    and returns the user data.
    
    Args:
        credentials: HTTP Bearer credentials from the request
        
    Returns:
        Dictionary containing user data from the token
        
    Raises:
        401: If token is missing, invalid, or expired
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Verify the access token
    payload = verify_token(token, token_type="access")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = security
) -> Optional[dict]:
    """
    Dependency to optionally get the current authenticated user.
    
    Similar to get_current_user but doesn't raise an exception if no token is provided.
    Useful for endpoints that can work with or without authentication.
    
    Args:
        credentials: HTTP Bearer credentials from the request (optional)
        
    Returns:
        Dictionary containing user data if token is valid, None otherwise
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = verify_token(token, token_type="access")
    
    return payload
