"""
SQL tool - executes SQL queries against workbook data.
"""

from __future__ import annotations

from typing import Any

from app.database.schema_manager import SchemaManager
from app.tools.base_tool import BaseTool


class SQLTool(BaseTool):
    """Tool for executing SQL queries."""

    def __init__(self) -> None:
        self.schema_manager = SchemaManager()

    @property
    def name(self) -> str:
        return "sql_query"

    @property
    def description(self) -> str:
        return "Execute a SQL query against a workbook sheet. Parameters: session_id, sheet_name, sql"

    def execute(self, session_id: str, sheet_name: str, sql: str, **kwargs: Any) -> dict[str, Any]:
        result = self.schema_manager.execute_query(session_id, sheet_name, sql)
        return {
            "row_count": result.height,
            "columns": result.columns,
            "data": result.head(100).to_dicts(),
        }