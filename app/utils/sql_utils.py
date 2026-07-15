"""
SQL utility functions.
"""

from __future__ import annotations

import re


def sanitize_sql(sql: str) -> str:
    """
    Basic SQL sanitization.
    Remove dangerous operations like DROP, DELETE, INSERT, UPDATE, etc.
    """
    sql_upper = sql.upper().strip()
    dangerous = ["DROP ", "DELETE ", "INSERT ", "UPDATE ", "ALTER ", "CREATE ", "TRUNCATE "]
    for d in dangerous:
        if d in sql_upper:
            raise ValueError(f"Dangerous SQL operation detected: {d}")
    return sql


def extract_table_name(sql: str) -> str | None:
    """Extract the table name from a SELECT query."""
    match = re.search(r"FROM\s+(\w+)", sql, re.IGNORECASE)
    return match.group(1) if match else None