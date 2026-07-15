"""
Upload-related request/response schemas.
"""

from typing import Any

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Response after uploading a workbook."""

    success: bool = True
    session_id: str = Field(...)
    file_name: str
    file_size: int
    sheet_count: int
    sheets: list[dict[str, Any]] = Field(default_factory=list, description="List of sheet names and row/column counts")
    message: str = "Workbook uploaded successfully."


class MultiUploadResponse(BaseModel):
    """Response after uploading multiple workbooks."""

    success: bool = True
    sessions: list[UploadResponse]
    total_files: int
    message: str = "All workbooks uploaded successfully."