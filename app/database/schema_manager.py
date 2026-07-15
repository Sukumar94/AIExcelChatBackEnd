"""
Schema management for DuckDB.
Handles creating, updating, and dropping tables/views.
"""

from __future__ import annotations

import logging
import re
from typing import Any

import polars as pl

from app.database.connection import DatabaseManager
from app.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class SchemaManager:
    """Manages DuckDB schemas for workbook data."""

    def __init__(self) -> None:
        self.db = DatabaseManager()

    def create_workbook_schema(self, session_id: str, sheets: dict[str, pl.DataFrame]) -> None:
        """
        Register all sheets from a workbook as DuckDB views.
        View names are prefixed with the session_id to avoid collisions.
        """
        for sheet_name, df in sheets.items():
            view_name = self._view_name(session_id, sheet_name)
            self.db.register_table(view_name, df)
            row_count = df.height
            logger.info("Registered view '%s' with %d rows", view_name, row_count)

    def drop_workbook_schema(self, session_id: str, sheet_names: list[str]) -> None:
        """Drop all views for a given session."""
        for sheet_name in sheet_names:
            view_name = self._view_name(session_id, sheet_name)
            self.db.unregister_table(view_name)
            logger.info("Dropped view '%s'", view_name)

    def execute_query(self, session_id: str, sheet_name: str, sql: str) -> pl.DataFrame:
        """
        Execute a SQL query against a specific sheet's view.
        The query is automatically scoped to the correct view.
        
        Security: Uses parameterized view names to prevent SQL injection.
        """
        # Validate inputs
        if not session_id or not isinstance(session_id, str):
            raise ValidationError("Invalid session ID")
        if not sheet_name or not isinstance(sheet_name, str):
            raise ValidationError("Invalid sheet name")
        if not sql or not isinstance(sql, str):
            raise ValidationError("Invalid SQL query")
        
        # Only allow SELECT statements for security
        if not sql.strip().upper().startswith("SELECT"):
            raise ValidationError("Only SELECT queries are allowed")
        
        view_name = self._view_name(session_id, sheet_name)
        
        # SQL should already have the correct view name from agent generation
        # Only replace if the original sheet_name is found (not part of a longer identifier)
        import re
        # Use word boundary to avoid replacing SalesData in session_123_SalesData
        pattern = r'\b' + re.escape(sheet_name) + r'\b'
        scoped_sql = re.sub(pattern, view_name, sql)
        
        logger.debug("Executing query for session %s, sheet %s", session_id[:8], sheet_name)
        result = self.db.query_to_df(scoped_sql)
        return result

    def get_sheet_preview(self, session_id: str, sheet_name: str, limit: int = 100) -> pl.DataFrame:
        """Get a preview of the sheet data."""
        view_name = self._view_name(session_id, sheet_name)
        return self.db.query_to_df(f"SELECT * FROM {view_name} LIMIT {limit}")

    def get_sheet_stats(self, session_id: str, sheet_name: str) -> dict[str, Any]:
        """Get summary statistics for a sheet."""
        view_name = self._view_name(session_id, sheet_name)
        stats = {}
        try:
            # Row count
            result = self.db.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()
            stats["row_count"] = result[0]

            # Column info
            cols = self.db.execute(
                f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{view_name}'"
            ).pl()
            stats["columns"] = cols.to_dicts()

            # Numeric column stats
            numeric_cols = [
                c["column_name"]
                for c in stats["columns"]
                if c["data_type"] in ("INTEGER", "BIGINT", "DOUBLE", "FLOAT", "DECIMAL", "HUGEINT")
            ]
            for col in numeric_cols:
                try:
                    agg = self.db.execute(
                        f"SELECT MIN({col}), MAX({col}), AVG({col}), STDDEV({col}) FROM {view_name}"
                    ).pl()
                    stats[f"{col}_stats"] = agg.to_dicts()[0]
                except Exception:
                    pass
        except Exception as e:
            logger.warning("Failed to compute stats for %s: %s", view_name, e)
        return stats

    @staticmethod
    def _view_name(session_id: str, sheet_name: str) -> str:
        """Generate a safe DuckDB view name."""
        safe_sheet = "".join(c if c.isalnum() else "_" for c in sheet_name)
        return f"session_{session_id[:8]}_{safe_sheet}"