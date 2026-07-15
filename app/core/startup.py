"""
Application startup lifecycle hooks.
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.database.connection import DatabaseManager

logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """Factory that creates and configures the FastAPI app."""
    setup_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    # ---- Lifecycle ----
    @app.on_event("startup")
    async def on_startup() -> None:
        logger.info("Starting %s v%s", settings.app_name, settings.app_version)
        # Ensure data directories exist
        for path_str in [
            settings.upload_path,
            settings.parquet_path,
            settings.duckdb_path,
            settings.faiss_path,
            settings.report_path,
            settings.chart_path,
            settings.temp_path,
        ]:
            Path(path_str).parent.mkdir(parents=True, exist_ok=True)
            Path(path_str).mkdir(parents=True, exist_ok=True)
        # Init DuckDB
        db = DatabaseManager()
        db.initialize()
        logger.info("DuckDB initialized at %s", settings.duckdb_path)

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        logger.info("Shutting down %s", settings.app_name)
        DatabaseManager().close()

    return app