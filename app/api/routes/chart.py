"""
Chart routes - generate and retrieve charts.
"""

from __future__ import annotations

from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_chart_service
from app.models.chart import ChartConfig, ChartResponse
from app.services.chart_service import ChartService


class ChartType(str, Enum):
    """Valid chart types."""
    BAR = "bar"
    LINE = "line"
    SCATTER = "scatter"
    PIE = "pie"
    HISTOGRAM = "histogram"
    BOX = "box"


router = APIRouter(
    prefix="/api/v1/chart",
    tags=["Charts"],
)


@router.post("/generate", response_model=ChartResponse)
async def generate_chart(
    session_id: str = Query(..., min_length=1),
    chart_type: ChartType = Query(...),
    title: str = Query("Chart", max_length=200),
    x_axis: str = Query(..., min_length=1),
    y_axis: str | None = Query(None, min_length=1),
    sheet_name: str | None = Query(None, min_length=1),
    chart_service: ChartService = Depends(get_chart_service),
):
    """Generate a chart from workbook data."""
    try:
        if not session_id or not x_axis:
            raise HTTPException(status_code=400, detail="session_id and x_axis are required")
        
        config = ChartConfig(
            chart_type=chart_type.value,
            title=title,
            x_axis=x_axis,
            y_axis=y_axis,
        )
        return chart_service.generate_chart(session_id, config, sheet_name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chart generation failed",
        )


@router.get("/auto/{session_id}", response_model=list[ChartResponse])
async def auto_charts(
    session_id: str,
    sheet_name: str | None = Query(None, min_length=1),
    chart_service: ChartService = Depends(get_chart_service),
):
    """Auto-generate recommended charts for a workbook."""
    try:
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id is required")
        return chart_service.auto_chart(session_id, sheet_name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))