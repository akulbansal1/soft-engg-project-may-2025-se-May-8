from sqlalchemy.orm import Session
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate, UserLogin, UserSession
from src.core.config import settings
from src.utils.cache import Cache

from typing import List, Optional
import secrets
import datetime

class UserService:
    """
    🔐 User Service for core user operations
    
    Functions: user registration, login, logout, session issuing
    """
    
    @staticmethod
    def register_user(db: Session, user: UserCreate) -> User:
        """
        User registration function
        Creates a new user in the database
        """
        # Check if user already exists
        existing_user = UserService.get_user_by_phone(db, user.phone)
        if existing_user:
            raise ValueError("User with this phone number already exists")
        
        # Create new user
        db_user = User(
            name=user.name, 
            phone=user.phone,
            is_active=user.is_active
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def login_user(db: Session, user_login: UserLogin) -> Optional[User]:
        """
        User login function
        Validates user existence and prepares for authentication
        (Authentication logic will be implemented later with passkey)
        """
        user = UserService.get_user_by_phone(db, user_login.phone)
        if not user:
            return None
        
        # Check if user is active
        if not user.is_active:
            return None
        
        # TODO: Add passkey authentication logic here
        return user
    
    @staticmethod
    def logout_user(user_id: int, session_token: str) -> bool:
        """
        User logout function
        Invalidates user session
        (Session management logic to be implemented)
        """
        # TODO: Implement session invalidation logic
        print(f"Logging out user {user_id} with session {session_token}")
        return True
    
    @staticmethod
    def issue_session(user_id: int) -> dict:
        """
        Session issuing function
        Creates a new session token for authenticated user
        """
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.datetime.now() + settings.SESSION_TOKEN_EXPIRY
        
        session_data = UserSession(
            user_id=user_id,
            session_token=session_token,
            expires_at=expires_at,
            created_at=datetime.datetime.now()
        )

        ## NOTE: Convert the SESSION_TOKEN_EXPIRY to a seconds 
        Cache.set(f"session:{user_id}", session_data, settings.SESSION_TOKEN_EXPIRY)
        
        print(f"Session issued for user {user_id}: {session_token}")
        return session_data
    
    # Method to activate user
    @staticmethod
    def activate_user(db: Session, user_id: int) -> Optional[User]:
        """Activate a user by ID"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        
        db_user.is_active = True
        db.commit()
        db.refresh(db_user)
        return db_user
    
    # Helper methods for CRUD operations
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_phone(db: Session, phone: int) -> Optional[User]:
        """Get user by phone number"""
        return db.query(User).filter(User.phone == phone).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_active_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users with pagination"""
        return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user information"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete a user"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True
