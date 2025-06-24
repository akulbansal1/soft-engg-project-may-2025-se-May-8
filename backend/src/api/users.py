from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.db.database import get_db
from src.services.user_service import UserService
from src.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin, UserSession
from src.utils.cache import Cache

router = APIRouter(prefix="/users", tags=["🔐 Users"])

## TODO: Might wanna gate this endpoint with authentication to prevent DOS attacks
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

## TODO: Might wanna gate this endpoint with authentication to prevent DOS attacks
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

## TODO: Implement this endpoint properly with the right authentication setting
# @router.put("/{user_id}", response_model=UserResponse)
# def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
#     """Update user information"""
#     updated_user = UserService.update_user(db, user_id, user_update)
#     if not updated_user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     # Clear cache
#     Cache.clear_pattern("users_list_*")
    
#     return updated_user