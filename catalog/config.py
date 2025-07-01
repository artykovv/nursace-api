from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database Configuration
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    
    # Service Configuration
    SERVICE_HOST: str = "0.0.0.0"
    SERVICE_PORT: int = 8000
    
    # Storage Service Configuration
    STORAGE_SERVICE_URL: str = "http://storage-service:8000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings() 