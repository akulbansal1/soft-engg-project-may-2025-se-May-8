from fastapi import APIRouter
from .users import router as users_router
from .auth import router as auth_router
from .emergency_contacts import router as emergency_contacts_router
from .medicines import router as medicines_router
from .documents import router as documents_router
from .doctors import router as doctors_router
from .appointments import router as appointments_router

api_router = APIRouter()

# Include all API routers
api_router.include_router(users_router)
api_router.include_router(auth_router)
api_router.include_router(emergency_contacts_router)
api_router.include_router(medicines_router)
api_router.include_router(documents_router)
api_router.include_router(doctors_router)
api_router.include_router(appointments_router)

__all__ = ["api_router"]
