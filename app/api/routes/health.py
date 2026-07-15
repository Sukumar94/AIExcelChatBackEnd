"""
Health check routes.
"""

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(
    prefix="/api/v1",
    tags=["Health"],
)


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "application": settings.app_name,
        "version": settings.app_version,
    }