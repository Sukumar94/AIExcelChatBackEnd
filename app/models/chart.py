"""
Chart-related data models.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ChartConfig(BaseModel):
    """Configuration for generating a chart."""

    chart_type: str = Field(description="Type of chart: bar, line, pie, scatter, histogram, box, heatmap")
    title: str = Field(default="Chart")
    x_axis: str | None = Field(default=None, description="Column name for X axis")
    y_axis: str | list[str] | None = Field(default=None, description="Column name(s) for Y axis")
    color: str | None = Field(default=None, description="Column for color grouping")
    aggregation: str | None = Field(default=None, description="Aggregation: sum, avg, count, min, max")
    width: int = Field(default=800)
    height: int = Field(default=500)


class ChartResponse(BaseModel):
    """Response containing chart data."""

    chart_json: dict[str, Any] = Field(description="Plotly figure JSON")
    chart_type: str
    title: str
    insights: str | None = Field(default=None, description="AI-generated insights about the chart")