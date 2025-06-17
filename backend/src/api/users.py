from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.db.database import get_db
from src.services.user_service import UserService
from src.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin, UserSession
from src.utils.cache import Cache

router = APIRouter(prefix="/users", tags=["🔐 Users"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    User Registration
    Creates a new user account
    """
    try:
        db_user = UserService.register_user(db, user)
        # Clear users cache
        Cache.clear_pattern("users_list_*")
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=dict)
def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    User Login
    Authenticates user and issues session
    (Passkey authentication to be implemented)
    """
    user = UserService.login_user(db, user_login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or invalid credentials"
        )
    
    # Issue session token
    session_data = UserService.issue_session(user.id)
    
    return {
        "message": "Login successful",
        "user": UserResponse.from_orm(user),
        "session": session_data
    }

@router.post("/logout")
def logout_user(user_id: int, session_token: str):
    """
    User Logout
    Invalidates user session
    """
    success = UserService.logout_user(user_id, session_token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to logout user"
        )
    
    return {"message": "Logout successful"}

@router.post("/session/{user_id}", response_model=dict)
def issue_session(user_id: int, db: Session = Depends(get_db)):
    """
    Session Issuing
    Creates a new session for authenticated user
    """
    # Verify user exists
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    session_data = UserService.issue_session(user_id)
    return {
        "message": "Session issued successfully",
        "session": session_data
    }

# Additional Helper Endpoints

@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users with caching"""
    cache_key = f"users_list_{skip}_{limit}"
    
    # Try to get from cache first
    cached_users = Cache.get(cache_key)
    if cached_users:
        return cached_users
    
    # Get from database
    users = UserService.get_users(db, skip=skip, limit=limit)
    
    # Convert to response format and cache for 5 minutes
    users_data = [UserResponse.from_orm(user) for user in users]
    Cache.set(cache_key, [user.dict() for user in users_data], expiry=300)
    
    return users_data

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update user information"""
    updated_user = UserService.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Clear cache
    Cache.clear_pattern("users_list_*")
    
    return updated_user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user"""
    success = UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Clear cache
    Cache.clear_pattern("users_list_*")
    
    return {"message": "User deleted successfully"}
