"""
JWT Utility Functions
Handles creation and verification of JWT tokens
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "your-refresh-secret-key-change-this")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
ALGORITHM = "HS256"


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing user data to encode in the token
        
    Returns:
        Encoded JWT access token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: Dictionary containing user data to encode in the token
        
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: The JWT token string to verify
        token_type: Type of token - 'access' or 'refresh'
        
    Returns:
        Decoded token payload if valid, None if invalid
    """
    try:
        # Use appropriate secret key based on token type
        secret_key = JWT_SECRET_KEY if token_type == "access" else JWT_REFRESH_SECRET_KEY
        
        # Decode the token
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        
        # Verify token type matches
        if payload.get("type") != token_type:
            return None
        
        return payload
    except JWTError:
        return None


def get_token_expiry(token_type: str = "access") -> datetime:
    """
    Get the expiration datetime for a token type.
    
    Args:
        token_type: Type of token - 'access' or 'refresh'
        
    Returns:
        Datetime when the token will expire
    """
    if token_type == "access":
        return datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        return datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
