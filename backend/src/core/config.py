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
    SECRET_KEY = os.getenv("SECRET_KEY")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    API_V1_STR = "/api/v1"
    PROJECT_NAME = "SE Project API"

    # Frontend Domain 
    FRONTEND_RP_ID = os.getenv("FRONTEND_RP_ID", "localhost:3000")
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    # Session and cache settings
    CHALLENGE_TIMEOUT = int(timedelta(minutes=5).total_seconds()*1000)  # 5 minutes in milliseconds
    CHALLENGE_CACHE_EXPIRY = int(timedelta(minutes=10).total_seconds())  # 10 minutes in seconds

    SESSION_TOKEN_EXPIRY = timedelta(hours=24*7) # 7 days

    COOKIE_EXPIRY = timedelta(days=7)  # 7 days
    COOKIE_SECURE = False # Set to True in production with HTTPS
    
    # Twilio SMS Configuration
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
    
    # SMS Verification Settings
    SMS_VERIFICATION_ENABLED = os.getenv("SMS_VERIFICATION_ENABLED", "True").lower() == "true"
    SMS_VERIFICATION_CODE_LENGTH = 6
    SMS_VERIFICATION_EXPIRY = int(timedelta(minutes=10).total_seconds())  # 10 minutes
    SMS_VERIFICATION_CACHE_EXPIRY = int(timedelta(hours=24).total_seconds())  # 24 hours for verified status

    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "eu-north-1")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "iitm-se-project")

    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

    # Celery
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

    AUTH_FREE_PATHS = [
        "/api/v1/",
        "/api/v1/health",
        "/api/v1/openapi.json",
        "/docs",
        "/redoc",
        "/api/v1/auth/sms/send",
        "/api/v1/auth/sms/verify",
        "/api/v1/auth/sms/status",
        "/api/v1/auth/passkey/register/challenge",
        "/api/v1/auth/passkey/register/verify",
        "/api/v1/auth/passkey/login/challenge",
        "/api/v1/auth/passkey/login/verify",
    ]

    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in environment variables")

    ADMIN_SESSION_TOKEN = SECRET_KEY

settings = Settings()