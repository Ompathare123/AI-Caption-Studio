"""
AI Caption Studio Backend API Entry Point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Caption Studio API",
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


@app.get("/")
async def health_check():
    """
    Health check endpoint to verify that the API server is running.
    
    Returns:
        dict: A dictionary containing the application status and project name.
    """
    return {
        "status": "running",
        "project": "AI Caption Studio"
    }
