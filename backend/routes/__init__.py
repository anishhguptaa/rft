"""
Backend Routes Package
Aggregates all backend route modules
"""

from fastapi import APIRouter
from .users_routes import router as users_router
from .login_routes import router as login_router

# Create main backend router
router = APIRouter()

# Include all sub-routers
router.include_router(users_router, tags=["Users"])
router.include_router(login_router, tags=["Authentication"])
