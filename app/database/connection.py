"""
DuckDB connection manager.
Provides a singleton connection to DuckDB for analytics queries.
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any

import duckdb

from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Thread-safe singleton DuckDB connection manager."""

    _instance: DatabaseManager | None = None
    _lock = threading.Lock()
    _conn: duckdb.DuckDBPyConnection | None = None
    _max_retries = 3

    def __new__(cls) -> DatabaseManager:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self) -> None:
        """Create or connect to the DuckDB database with retry logic and fallback."""
        if self._conn is not None:
            return
        
        db_path = Path(settings.duckdb_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Retry logic for database locks
        for attempt in range(self._max_retries):
            try:
                import time
                self._conn = duckdb.connect(
                    str(db_path),
                    read_only=False,
                    config={'threads': 4, 'memory_limit': '2GB'}
                )
                # Load parquet extension; install only if it is missing.
                try:
                    self._conn.execute("LOAD 'parquet';")
                except Exception:
                    self._conn.execute("INSTALL 'parquet';")
                    self._conn.execute("LOAD 'parquet';")
                self._conn.execute("SET threads TO 4;")
                self._conn.execute("SET memory_limit = '2GB';")
                logger.info("DuckDB connected: %s", db_path)
                return
            except Exception as e:
                if attempt < self._max_retries - 1:
                    wait_time = 2 + (attempt * 2)  # 2s, 4s, 6s
                    logger.warning(
                        "Database connection attempt %d/%d failed, retrying in %ds: %s",
                        attempt + 1, self._max_retries, wait_time, e
                    )
                    time.sleep(wait_time)
                else:
                    logger.error("Failed to connect to database after %d attempts: %s", self._max_retries, e)
                    logger.info("Attempting read-only fallback mode...")
                    try:
                        # Fallback: Use read-only mode if writable connection fails
                        self._conn = duckdb.connect(str(db_path), read_only=True)
                        logger.warning("Connected in READ-ONLY mode. Some operations may be limited.")
                        return
                    except Exception as fallback_error:
                        logger.critical("Failed to connect even in read-only mode: %s", fallback_error)
                        raise

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        """Get the active connection."""
        if self._conn is None:
            self.initialize()
        return self._conn  # type: ignore

    def execute(self, query: str, params: list[Any] | None = None) -> duckdb.DuckDBPyRelation:
        """Execute a SQL query and return the result relation."""
        if params:
            return self.conn.execute(query, params)
        return self.conn.execute(query)

    def query_to_df(self, query: str, params: list[Any] | None = None) -> Any:
        """Execute query and return as a DataFrame (Polars or Pandas)."""
        return self.execute(query, params).pl()

    def register_table(self, name: str, df: Any) -> None:
        """Register a Polars DataFrame as a DuckDB view."""
        self.conn.register(name, df)

    def unregister_table(self, name: str) -> None:
        """Drop a registered view."""
        self.conn.execute(f"DROP VIEW IF EXISTS {name}")

    def table_exists(self, name: str) -> bool:
        """Check if a table or view exists."""
        result = self.conn.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = ?",
            [name],
        ).fetchone()
        return result[0] > 0

    def close(self) -> None:
        """Close the DuckDB connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.info("DuckDB connection closed.")