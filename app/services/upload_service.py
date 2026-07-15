"""
Upload service - coordinates the full upload workflow.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import UploadFile

from app.database.metadata_store import MetadataStore
from app.database.schema_manager import SchemaManager
from app.excel.cleaner import DataCleaner
from app.excel.metadata import MetadataExtractor
from app.excel.normalizer import DataNormalizer
from app.excel.parquet_converter import ParquetConverter
from app.excel.parser import ExcelParser
from app.excel.session_builder import SessionBuilder
from app.excel.validator import ExcelValidator
from app.models.session import SessionModel
from app.services.session_service import SessionService

logger = logging.getLogger(__name__)


class UploadService:
    """Handles workbook uploads with full processing pipeline."""

    def __init__(self) -> None:
        self.schema_manager = SchemaManager()
        self.metadata_store = MetadataStore()

    async def upload(self, file: UploadFile) -> dict[str, Any]:
        """
        Upload and process an Excel workbook.
        Returns session info dict.
        """
        # 1. Validate
        await ExcelValidator.validate(file)

        file_size = file.size or 0

        # 2. Parse
        sheets = await ExcelParser.parse(file)

        # 3. Clean & normalize each sheet
        cleaned_sheets = {}
        for name, df in sheets.items():
            df = DataCleaner.clean_dataframe(df)
            df = DataNormalizer.normalize_dataframe(df)
            cleaned_sheets[name] = df

        # 4. Build session
        session = SessionBuilder.build_session(
            file_name=file.filename or "unknown",
            file_size=file_size,
            sheets=cleaned_sheets,
        )

        # 5. Store in memory
        SessionService.create_session(session)

        # 6. Register in DuckDB for SQL queries
        self.schema_manager.create_workbook_schema(session.session_id, cleaned_sheets)

        # 7. Save metadata
        sheets_info = MetadataExtractor.extract_all_sheets(cleaned_sheets)
        self.metadata_store.save_workbook_metadata(
            session_id=session.session_id,
            file_name=session.metadata.file_name,
            file_size=file_size,
            sheet_count=session.metadata.total_sheets,
            sheets_info=sheets_info,
        )

        # 8. Save as Parquet for persistence
        for name, df in cleaned_sheets.items():
            ParquetConverter.to_parquet(df, session.session_id, name)

        logger.info(
            "Upload complete: %s (%d sheets, %d rows total)",
            session.metadata.file_name,
            session.metadata.total_sheets,
            sum(s.rows for s in session.sheets.values()),
        )

        return {
            "session_id": session.session_id,
            "file_name": session.metadata.file_name,
            "file_size": file_size,
            "sheet_count": session.metadata.total_sheets,
            "sheets": sheets_info,
        }

    async def upload_multiple(self, files: list[UploadFile]) -> list[dict[str, Any]]:
        """Upload multiple files."""
        results = []
        for file in files:
            try:
                result = await self.upload(file)
                results.append(result)
            except Exception as e:
                logger.error("Failed to upload %s: %s", file.filename, e)
                results.append({
                    "session_id": None,
                    "file_name": file.filename or "unknown",
                    "error": str(e),
                })
        return results