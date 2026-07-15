"""
Dashboard routes - aggregated data views.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_dashboard_service
from app.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard"],
)


@router.get("/{session_id}")
async def get_dashboard(
    session_id: str,
    dashboard_service: DashboardService = Depends(get_dashboard_service),
):
    """Get full dashboard data for a session."""
    try:
        return dashboard_service.get_dashboard_data(session_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("")
async def list_recent_sessions(
    limit: int = Query(10, ge=1, le=50),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
):
    """List recent workbook sessions."""
    return dashboard_service.list_recent_sessions(limit=limit)