from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.db.database import get_db
from src.services.user_service import UserService
from src.schemas.user import  UserResponse, UserSession

from src.core.auth_middleware import RequireAuth, RequireOwnership

router = APIRouter(prefix="/users", tags=["🔐 Users"])

@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user = Depends(RequireAuth)):
    """Get all users with caching"""
    
    # Get from database
    users = UserService.get_users(db, skip=skip, limit=limit)
    
    # Convert to response format and cache for 5 minutes
    users_data = [UserResponse.model_validate(user) for user in users]

    return users_data

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), user = Depends(RequireOwnership)):
    """Get user by ID"""
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)

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