from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.db.database import engine, Base
from src.api import api_router
from src.core.config import settings
from src.core.auth_middleware import RequireAuth, OptionalAuth

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI backend with PostgreSQL, Redis, and Celery",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    contact={
        "name": "SE Project Team",
        "email": "team@example.com"
    },
    license_info={
        "name": "MIT License"
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get(settings.API_V1_STR + "/")
def read_root():
    """Health check endpoint"""
    return {"message": "Backend is running!", "status": "ok", "version": "1.0.0"}

@app.get(settings.API_V1_STR + "/health")
def health_check():
    """Health check for monitoring"""
    return {"status": "healthy", "service": "backend-api"}

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)