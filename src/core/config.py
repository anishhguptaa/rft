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

    # Database
    DATABASE_URL: str = Field(description="Database URL")
    
    # JWT Authentication
    JWT_SECRET_KEY: str = Field(description="JWT secret key for access tokens")
    JWT_REFRESH_SECRET_KEY: str = Field(description="JWT secret key for refresh tokens")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration in minutes")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiration in days")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
