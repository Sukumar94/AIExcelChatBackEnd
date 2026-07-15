"""
Report routes - generate reports from workbook data.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_report_service
from app.services.report_service import ReportService

router = APIRouter(
    prefix="/api/v1/report",
    tags=["Reports"],
)


@router.get("/{session_id}")
async def generate_report(
    session_id: str,
    sheet_name: str | None = Query(None),
    include_charts: bool = Query(True),
    report_service: ReportService = Depends(get_report_service),
):
    """Generate a report from workbook data."""
    try:
        return report_service.generate_report(session_id, sheet_name, include_charts)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))