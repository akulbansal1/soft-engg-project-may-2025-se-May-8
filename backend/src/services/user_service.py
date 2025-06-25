from sqlalchemy.orm import Session
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate, UserLogin, UserSession
from src.core.config import settings
from src.utils.cache import Cache

from typing import List, Optional
import secrets
import datetime
import json

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
        
        return user
    
    @staticmethod
    def logout_user(db: Session, user_id: int, session_token: str) -> bool:
        """
        User logout function
        Invalidates user session
        (Session management logic to be implemented)
        """

        user = UserService.get_user_by_session(db, session_token=session_token)

        if not user or user.id != user_id:
            print(f"User ID mismatch or user not found for session {session_token}")
            return False
        
        # Invalidate session
        Cache.delete(f"session_{session_token}")

        print(f"Logging out user {user_id} with session {session_token}")
        return True
    
    @staticmethod
    def logout_user_by_token(session_token: str) -> bool:
        """
        User logout function using session token
        Invalidates user session by token
        """
      
        # For now, we'll store in Cache with expiry
        Cache.delete(f"session_{session_token}")
        print(f"Logged out session: {session_token}")
        return True
    
    @staticmethod
    def issue_session(user_id: int) -> dict:
        """
        Session issuing function
        Creates a new session token for authenticated user
        """
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.datetime.now() + settings.SESSION_TOKEN_EXPIRY
        
        session_data = {
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": expires_at.isoformat(),
            "created_at": datetime.datetime.now().isoformat()
        }

        Cache.set(f"session_{session_token}", json.dumps(session_data), expiry=settings.SESSION_TOKEN_EXPIRY.total_seconds())
        
        print(f"Session issued for user {user_id}: {session_token}")
        return session_data
    
    @staticmethod
    def get_user_by_session(db: Session, session_token: str) -> Optional[User]:
        """
        Get user by session token
        """        
        try:
            user_id = UserService.validate_session(db, session_token)
            if not user_id:
                return None
            
            # Get user by ID
            user = UserService.get_user_by_id(db, user_id)
            if user and user.is_active:
                return user
                
        except (json.JSONDecodeError, ValueError):
            Cache.delete(f"session_{session_token}")
            
        return None
    
    @staticmethod
    def activate_user(db: Session, user_id: int) -> bool:
        """
        Activate a user account
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.is_active = True
        db.commit()
        return True
    
    @staticmethod
    def validate_session(db: Session, session_token: str) -> Optional[int]:
        """
        Validate session token and return user if valid
        This is the main method for session authentication
        """
        if not session_token:
            return None
        
        session_data_json = Cache.get(f"session_{session_token}")
        if not session_data_json:
            return None
        
        try:
            session_data = json.loads(session_data_json)
            user_id = session_data.get("user_id")
            expires_at_str = session_data.get("expires_at")
            
            # Check if session has expired
            if expires_at_str:
                expires_at = datetime.datetime.fromisoformat(expires_at_str)
                if datetime.datetime.now() > expires_at:
                    Cache.delete(f"session_{session_token}")
                    return None
            
            return user_id
                
        except (json.JSONDecodeError, ValueError):
            Cache.delete(f"session_{session_token}")
            
        return None
    
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
