"""
Core Configuration Settings
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""

    # App Info
    PROJECT_NAME: str = Field(description="Project name")
    DEBUG: bool = Field(description="Debug mode")
    
    # Server
    HOST: str = Field(description="Server host")
    PORT: int = Field(description="Server port")

    # Third Party API Keys
    GEMINI_API_KEY: str = Field(description="Gemini API key")

    # CORS
    ALLOWED_ORIGINS: List[str] = Field(description="Allowed origins for CORS")

    DATABASE_URL: str = Field(description="Database URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
