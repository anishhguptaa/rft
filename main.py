"""
FastAPI Main Application
This is the entry point for the FastAPI application with AI and Backend endpoints.
"""

import sys
from pathlib import Path

# Add src directory to Python path so internal imports work
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from core.config import settings
from core.db import engine, get_db
from models.DbModels.user import Base
from api.modules.auth.routers import router as auth_router
from api.modules.user.routers import router as user_router
from api.modules.ai_backend_integration.routers import router as ai_backend_router
from api.modules.daily_schedule.routers import router as daily_schedule_router
from api.modules.workout.routers import router as workout_router
from middleware.auth_middleware import AuthenticationMiddleware

# Create all tables stored in the Base metadata
# This will create the 'users' table if it doesn't exist
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS (must be added before authentication middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Authentication Middleware (protects all endpoints except public routes)
app.add_middleware(AuthenticationMiddleware)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(ai_backend_router, prefix="/api/ai-backend", tags=["AI Backend Integration"])
app.include_router(daily_schedule_router, prefix="/api/daily-schedule", tags=["Daily Schedule"])
app.include_router(workout_router, prefix="/api/workout", tags=["Workout"])


# DB health endpoint (verifies app->DB connectivity)
@app.get("/db/health", tags=["Root"])
async def db_health(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        print("Database connection is healthy.")
        return {"status": "online", "message": "Database connection is healthy."}
    except Exception as e:
        print(f"Database connection failed: {e}")
        return {"status": "offline", "message": f"Database connection failed: {e}"}


@app.get("/health", tags=["Root"])
async def root():
    """Root endpoint - health check"""
    return {
        "status": "online",
        "message": "RFT App is running",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
