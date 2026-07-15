"""
Session Models

Represents an uploaded Excel workbook.
This model is reused throughout the application.

Author: AI Excel Analytics Platform
"""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any
from uuid import uuid4

import polars as pl
from pydantic import BaseModel, Field, ConfigDict


class SheetData(BaseModel):
    """
    Represents a single worksheet.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    sheet_name: str

    rows: int

    columns: int

    column_names: list[str]

    dataframe: pl.DataFrame


class WorkbookMetadata(BaseModel):
    """
    Workbook information.
    """

    file_name: str
    file_size: int = Field(default=0)
    total_sheets: int

    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SessionModel(BaseModel):
    """
    Active user session.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    session_id: str = Field(default_factory=lambda: str(uuid4()))

    metadata: WorkbookMetadata

    sheets: dict[str, SheetData] = Field(default_factory=dict)

    context: dict[str, Any] = Field(default_factory=dict)