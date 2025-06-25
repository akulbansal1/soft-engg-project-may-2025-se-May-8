import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Settings:
    """Application settings and configuration"""


    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # PostgreSQL specific settings (when using PostgreSQL)
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "college_project")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    
    @property
    def postgres_url(self) -> str:
        """Generate PostgreSQL URL from individual components"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database"""
        return self.DATABASE_URL.startswith("sqlite")
    
    @property 
    def is_postgres(self) -> bool:
        """Check if using PostgreSQL database"""
        return self.DATABASE_URL.startswith("postgresql")
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # App
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    API_V1_STR = "/api/v1"
    PROJECT_NAME = "SE Project API"

    # Frontend Domain 
    FRONTEND_RP_ID = os.getenv("FRONTEND_RP_ID", "localhost:3000")
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    CHALLENGE_TIMEOUT = int(timedelta(minutes=5).total_seconds() * 1000000)  # 5 minutes in microseconds
    CHALLENGE_CACHE_EXPIRY = int(timedelta(minutes=10).total_seconds())  # 10 minutes in seconds

    SESSION_TOKEN_EXPIRY = timedelta(hours=24*7) # 7 days

    COOKIE_EXPIRY = timedelta(days=7)  # 7 days
    COOKIE_SECURE = False # Set to True in production with HTTPS
    
    # Celery
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # CORS
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    AUTH_FREE_PATHS = [
        "/api/v1/",
        "/api/v1/health",
        "/api/v1/openapi.json",
        "/docs",
        "/redoc",
        "/api/v1/auth/passkey/register/challenge",
        "/api/v1/auth/passkey/register/verify",
        "/api/v1/auth/passkey/login/challenge",
        "/api/v1/auth/passkey/login/verify",
    ]


    ADMIN_SESSION_TOKEN = SECRET_KEY

settings = Settings()