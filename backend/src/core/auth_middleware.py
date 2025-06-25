from fastapi import HTTPException, status, Depends, Cookie, Request
from sqlalchemy.orm import Session
from typing import Optional, Annotated

from src.db.database import get_db
from src.services.user_service import UserService
from src.schemas.user import UserResponse
from src.models.user import User
from src.core.config import settings

class AuthMiddleware:
    """Authentication middleware for FastAPI routes"""
    
    @staticmethod
    def get_current_user(
        session_token: Annotated[Optional[str], Cookie()] = None,
        db: Session = Depends(get_db)
    ) -> User:
        """
        Dependency to get current authenticated user from session cookie
        Raises 401 if no valid session found
        """
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No session token provided",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = UserService.get_user_by_session(db, session_token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    
    @staticmethod
    def get_current_user_optional(
        session_token: Annotated[Optional[str], Cookie()] = None,
        db: Session = Depends(get_db)
    ) -> Optional[User]:
        """
        Dependency to optionally get current authenticated user
        Returns None if no valid session, doesn't raise exceptions
        """
        if not session_token:
            return None
        
        return UserService.get_user_by_session(db, session_token)

    @staticmethod
    def validate_user_ownership(
        user_id: int,
        current_user: User = Depends(get_current_user)
    ) -> User:
        """
        Dependency to validate that current user owns the resource
        Used for endpoints like /users/{user_id} where user can only access their own data
        """
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own resources"
            )
        return current_user
    
    @staticmethod
    def validate_admin_access(
        session_token: Annotated[Optional[str], Cookie()] = None 
    ) -> Optional[bool]:
        """
        Dependency to validate that current user is an admin
        Raises 403 if user is not an admin
        """
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No session token provided",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if session_token != settings.ADMIN_SESSION_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )
        
        return True
        
# Convenience aliases for easy import
RequireAuth = AuthMiddleware.get_current_user
OptionalAuth = AuthMiddleware.get_current_user_optional
RequireOwnership = AuthMiddleware.validate_user_ownership
RequireAdmin = AuthMiddleware.validate_admin_access

