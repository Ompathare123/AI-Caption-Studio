"""
AI Caption Studio Backend API Entry Point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.router import api_router
from backend.app.core.config import settings
from backend.app.core.errors import register_error_handlers
from backend.app.database.session import Base, engine

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API services for speech-to-text, caption generation, and video rendering.",
    version="1.0.0",
)

# Configure CORS Middleware (for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router, prefix=settings.API_PREFIX)

# Register global exception handlers
register_error_handlers(app)


@app.get("/")
async def health_check():
    """
    Health check endpoint to verify that the API server is running.

    Returns:
        dict: A dictionary containing the application status and project name.
    """
    return {"status": "running", "project": settings.APP_NAME}
