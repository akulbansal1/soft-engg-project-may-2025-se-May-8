from fastapi import APIRouter
from .users import router as users_router

api_router = APIRouter("/api/v1", tags=["API"])

# Include all API routers
api_router.include_router(users_router)

__all__ = ["api_router"]
