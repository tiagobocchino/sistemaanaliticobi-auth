"""
Application configuration using environment variables
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str

    # Application
    secret_key: str
    environment: str = "development"

    cvdw_base_url: str | None = None
    cvdw_api_key: str | None = None
    cvdw_email: str | None = None
    cvdw_account_id: str | None = None

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default port
        "http://localhost:5174",  # Alternate Vite port
        "http://localhost:8000",
        "http://localhost:8082",  # Expo web dev
        "http://localhost:8084",  # Expo web fallback
        "http://localhost:8085",  # Expo web fallback
    ]

    # JWT
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
