import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    TABLE_NAME: str
    
    class Config:
        env_file = ".env"

# Create settings instance
settings = Settings()
