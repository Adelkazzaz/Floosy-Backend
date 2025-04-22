from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API settings
    API_PREFIX: str = "/api"
    PORT: int = int(os.getenv("PORT", 8000))
    
    # Security settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "e9ba480a2499a0c0ff41e2cdcf4bebc4b2dea4dc77ca40ec1b9256537bbf68ae")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 86400  # 24 hours
    
    # Database settings
    MONGODB_URI: str = os.getenv("MONGODB_URI")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "floosy_db")
    
    # CORS settings
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    class Config:
        env_file = ".env"

settings = Settings()
