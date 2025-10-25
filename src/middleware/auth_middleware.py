"""
Authentication Middleware
Protects all API endpoints except public routes (auth endpoints and health checks)
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from core.jwt_utils import verify_token
from typing import List


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to verify JWT tokens for all protected endpoints.
    
    Public endpoints (excluded from authentication):
    - /api/auth/* (signup, login, refresh, logout)
    - /health (health check)
    - /db/health (database health check)
    - /docs (API documentation)
    - /redoc (API documentation)
    - /openapi.json (OpenAPI schema)
    """
    
    # Define public paths that don't require authentication
    PUBLIC_PATHS: List[str] = [
        "/api/auth/signup",
        "/api/auth/login",
        "/api/auth/refresh",
        "/api/auth/logout",
        "/health",
        "/db/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/"
    ]
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """
        Process each request and verify authentication for protected endpoints.
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            Response from the next handler or 401 error
        """
        # Get the request path
        path = request.url.path
        
        # Check if the path is public (no authentication required)
        if self._is_public_path(path):
            return await call_next(request)
        
        # Extract the access token from cookies
        access_token = request.cookies.get("access_token")
        
        if not access_token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Access token not found",
                    "message": "Please login to access this resource"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify the token
        payload = verify_token(access_token, token_type="access")
        
        if not payload:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Invalid or expired access token",
                    "message": "Please login again or refresh your token"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Attach user info to request state for use in route handlers
        request.state.user = payload
        request.state.user_id = payload.get("user_id")
        request.state.email = payload.get("email")
        
        # Continue to the next middleware or route handler
        return await call_next(request)
    
    def _is_public_path(self, path: str) -> bool:
        """
        Check if a path is public (doesn't require authentication).
        
        Args:
            path: The request path
            
        Returns:
            True if the path is public, False otherwise
        """
        # Check exact matches
        if path in self.PUBLIC_PATHS:
            return True
        
        # Check if path starts with any public prefix
        public_prefixes = ["/docs", "/redoc", "/openapi.json"]
        for prefix in public_prefixes:
            if path.startswith(prefix):
                return True
        
        return False
