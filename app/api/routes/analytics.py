"""
Analytics routes - data analysis endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_analytics_service
from app.services.analytics_service import AnalyticsService

router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["Analytics"],
)


@router.get("/summary/{session_id}")
async def get_summary(
    session_id: str,
    sheet_name: str | None = Query(None),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    """Get a comprehensive summary of the workbook data."""
    try:
        return analytics_service.get_summary(session_id, sheet_name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/column/{session_id}")
async def analyze_column(
    session_id: str,
    column: str = Query(...),
    sheet_name: str | None = Query(None),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    """Get detailed analysis of a specific column."""
    try:
        return analytics_service.get_column_analysis(session_id, column, sheet_name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/outliers/{session_id}")
async def detect_outliers(
    session_id: str,
    column: str = Query(...),
    sheet_name: str | None = Query(None),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    """Detect outliers in a numeric column."""
    try:
        return analytics_service.detect_outliers(session_id, column, sheet_name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))