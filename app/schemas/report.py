"""
Report-related request/response schemas.
"""

from typing import Any

from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    """Request to generate a report."""

    session_id: str = Field(...)
    sheet_name: str | None = Field(default=None)
    report_type: str = Field(default="summary", description="summary, detailed, custom")
    include_charts: bool = Field(default=True)
    format: str = Field(default="html", description="html, pdf, xlsx")


class ReportResponse(BaseModel):
    """Response containing report data."""

    report_html: str | None = None
    report_url: str | None = None
    insights: list[str] = Field(default_factory=list)
    charts: list[dict[str, Any]] = Field(default_factory=list)
    statistics: dict[str, Any] = Field(default_factory=dict)