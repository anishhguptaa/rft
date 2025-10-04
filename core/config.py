"""
Core Configuration Settings
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""

    # App Info
    PROJECT_NAME: str = Field(default="RFT App", description="Project name")
    DEBUG: bool = Field(default=True, description="Debug mode")

    # Server
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")

    # Third Party API Keys
    GEMINI_API_KEY: str = Field(description="Gemini API key")

    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed origins for CORS",
    )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
