"""
FastAPI Main Application
This is the entry point for the FastAPI application with AI and Backend endpoints.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from core.config import settings
from core.db import engine, get_db
from models.user import Base
from models.goal import Goal  # Import the new Goal model
from models.workout_plan import WorkoutPlan # Import the new WorkoutPlan model
from models.daily_workout import DailyWorkout # Import the new DailyWorkout model
from models.exercise import Exercise # Import the new Exercise model
from models.workout_log import WorkoutLog # Import the new WorkoutLog model
from models.meal_log import MealLog # Import the new MealLog model
from models.user_progress import UserProgress # Import the new UserProgress model
from ai.routes import router as ai_router
from backend.routes import router as backend_router

# Create all tables stored in the Base metadata
# This will create the 'users' table if it doesn't exist
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ai_router, prefix="/api/ai", tags=["AI"])
app.include_router(backend_router, prefix="/api/backend", tags=["Backend"])


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
