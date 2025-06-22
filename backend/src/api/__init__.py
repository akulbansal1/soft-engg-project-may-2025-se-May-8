from fastapi import APIRouter
from .users import router as users_router
from .auth import router as auth_router
from .emergency_contacts import router as emergency_contacts_router

api_router = APIRouter(tags=["API"])

# Include all API routers
api_router.include_router(users_router)
api_router.include_router(auth_router)
api_router.include_router(emergency_contacts_router)

__all__ = ["api_router"]
