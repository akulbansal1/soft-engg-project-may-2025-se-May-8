import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_user_registration():
    """Test user registration endpoint"""
    user_data = {
        "name": "John Doe",
        "email": "john.doe@example.com"
    }
    
    response = client.post("/api/v1/users/register", json=user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "created_at" in data

def test_user_login():
    """Test user login endpoint"""
    # First register a user
    user_data = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com"
    }
    client.post("/api/v1/users/register", json=user_data)
    
    # Then try to login
    login_data = {
        "email": "jane.doe@example.com"
    }
    
    response = client.post("/api/v1/users/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["message"] == "Login successful"
    assert "user" in data
    assert "session" in data
    assert data["user"]["email"] == login_data["email"]

def test_user_login_not_found():
    """Test login with non-existent user"""
    login_data = {
        "email": "nonexistent@example.com"
    }
    
    response = client.post("/api/v1/users/login", json=login_data)
    assert response.status_code == 401
    assert "User not found" in response.json()["detail"]

def test_duplicate_user_registration():
    """Test registration with duplicate email"""
    user_data = {
        "name": "Duplicate User",
        "email": "duplicate@example.com"
    }
    
    # Register first time
    response1 = client.post("/api/v1/users/register", json=user_data)
    assert response1.status_code == 201
    
    # Try to register again with same email
    response2 = client.post("/api/v1/users/register", json=user_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]
