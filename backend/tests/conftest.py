"""
Configuration for pytest testing
"""
import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from contextlib import asynccontextmanager

os.environ["SMS_VERIFICATION_ENABLED"] = "False"
os.environ["TESTING"] = "True"

from main import app
from src.db.database import Base, get_db

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def test_db():
    """Create a test database session with proper isolation"""
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
       
        db.close()

        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client():
    """Create a test client with test database"""
 
    Base.metadata.create_all(bind=engine)

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides = {}
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def test_settings():
    """Test configuration settings - creates a separate instance"""
    from src.core.config import Settings
    
    test_settings = Settings()
    test_settings.DATABASE_URL = SQLALCHEMY_DATABASE_URL
    test_settings.DEBUG = True
    test_settings.TESTING = True
    return test_settings

@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    from datetime import date
    return {
        "name": "Test User",
        "phone": "1234567890",
        "dob": date(1990, 1, 15),
        "gender": "Other"
    }

@pytest.fixture
def test_login_data():
    """Sample login data for testing"""
    return {
        "phone": "1234567890"
    }
