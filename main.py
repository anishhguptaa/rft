"""
FastAPI Main Application
This is the entry point for the FastAPI application with AI and Backend endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from ai.routes import router as ai_router
from backend.routes import router as backend_router

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

