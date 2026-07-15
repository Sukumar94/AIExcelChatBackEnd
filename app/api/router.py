"""
Main API router that aggregates all route modules.
"""

from fastapi import APIRouter

from app.api.routes.upload import router as upload_router
from app.api.routes.chat import router as chat_router
from app.api.routes.chart import router as chart_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.session import router as session_router
from app.api.routes.report import router as report_router
from app.api.routes.voice import router as voice_router
from app.api.routes.health import router as health_router
from app.api.routes.analytics import router as analytics_router

api_router = APIRouter()

api_router.include_router(upload_router)
api_router.include_router(chat_router)
api_router.include_router(chart_router)
api_router.include_router(dashboard_router)
api_router.include_router(session_router)
api_router.include_router(report_router)
api_router.include_router(voice_router)
api_router.include_router(health_router)
api_router.include_router(analytics_router)