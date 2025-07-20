
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import yaml

from src.db.database import engine, Base
from src.api import api_router
from src.core.config import settings
from src.core.auth_middleware import RequireAuth, OptionalAuth

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="SE Project API (Team 8, May 2025)",
    description=(
        "Backend API for Team 8's Software Engineering Project (May 2025 Term)\n"
        "This backend powers a web-based mobile application designed for senior citizens and their family caregivers. "
        "The application enhances daily living and care coordination through these core modules identified based on user stories:\n\n"
        "- Easy-to-use UI: Senior-friendly design with large text, bold colors, and simple navigation\n"
        "- Medicine Tracker: Prescription management and medication identification\n"
        "- Appointments Tracker: Book, view, and get reminders for doctor appointments\n"
        "- SOS: Emergency alert system for designated contacts\n"
        "- Documents Vault: Secure digital repository for medical reports and history\n"
    ),
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    contact={
        "name": "Github Repository",
        "url": "https://github.com/akulbansal1/soft-engg-project-may-2025-se-May-8"
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
    """
    Root API endpoint for service status. Returns a message confirming the backend is running, along with status and version info.
    """
    return {"message": "Backend is running!", "status": "ok", "version": "1.0.0"}

@app.get(settings.API_V1_STR + "/health")
def health_check():
    """
    Health check endpoint for monitoring tools. Returns a simple healthy status and service name.
    """
    return {"status": "healthy", "service": "backend-api"}

@app.get(settings.API_V1_STR + "/openapi.yaml", response_class=Response, include_in_schema=False)
def get_openapi_yaml():
    """
    Get OpenAPI specification in YAML format. This endpoint provides the same OpenAPI spec as /openapi.json but in YAML format.
    """
    openapi_spec = app.openapi()
    openapi_yaml = yaml.dump(openapi_spec, default_flow_style=False, sort_keys=False)
    return Response(content=openapi_yaml, media_type="application/x-yaml")

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