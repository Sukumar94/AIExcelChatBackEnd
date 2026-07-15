"""
Builds session models from parsed Excel data.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import polars as pl

from app.models.session import SessionModel, SheetData, WorkbookMetadata


class SessionBuilder:
    """Builds SessionModel instances from parsed workbook data."""

    @staticmethod
    def build_session(
        file_name: str,
        file_size: int,
        sheets: dict[str, pl.DataFrame],
    ) -> SessionModel:
        """Create a complete SessionModel from parsed sheets."""
        sheet_data: dict[str, SheetData] = {}
        for sheet_name, df in sheets.items():
            sheet_data[sheet_name] = SheetData(
                sheet_name=sheet_name,
                rows=df.height,
                columns=df.width,
                column_names=df.columns,
                dataframe=df,
            )

        metadata = WorkbookMetadata(
            file_name=file_name,
            file_size=file_size,
            total_sheets=len(sheets),
            uploaded_at=datetime.now(timezone.utc),
        )

        return SessionModel(
            session_id=str(uuid4()),
            metadata=metadata,
            sheets=sheet_data,
        )