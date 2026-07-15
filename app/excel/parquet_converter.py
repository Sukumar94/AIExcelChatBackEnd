"""
Converts Excel data to Parquet format for efficient storage and querying.
"""

from __future__ import annotations

import logging
from pathlib import Path

import polars as pl

from app.core.config import settings

logger = logging.getLogger(__name__)


class ParquetConverter:
    """Converts DataFrames to Parquet files."""

    @staticmethod
    def to_parquet(df: pl.DataFrame, session_id: str, sheet_name: str) -> str:
        """
        Save a DataFrame as a Parquet file.
        Returns the file path.
        """
        base_path = Path(settings.parquet_path)
        base_path.mkdir(parents=True, exist_ok=True)
        safe_name = "".join(c if c.isalnum() else "_" for c in sheet_name)
        file_path = base_path / f"{session_id[:8]}_{safe_name}.parquet"

        df.write_parquet(str(file_path), compression="zstd")
        logger.info("Saved Parquet: %s (%d rows)", file_path, df.height)
        return str(file_path)

    @staticmethod
    def from_parquet(file_path: str) -> pl.DataFrame:
        """Load a DataFrame from a Parquet file."""
        return pl.read_parquet(file_path)

    @staticmethod
    def session_parquet_paths(session_id: str) -> list[Path]:
        """List all Parquet files for a session."""
        base_path = Path(settings.parquet_path)
        return list(base_path.glob(f"{session_id[:8]}_*.parquet"))

    @staticmethod
    def cleanup_session(session_id: str) -> None:
        """Remove all Parquet files for a session."""
        for f in ParquetConverter.session_parquet_paths(session_id):
            f.unlink(missing_ok=True)
            logger.info("Deleted Parquet: %s", f)