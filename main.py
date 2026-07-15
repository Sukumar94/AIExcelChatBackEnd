"""
AI Excel Analytics Platform - Main Entry Point

A FastAPI application that provides AI-powered Excel data analysis,
charting, reporting, and natural language querying capabilities.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.database.connection import DatabaseManager
from app.middleware.exceptions import ExceptionHandlingMiddleware
from app.services.session_service import SessionService

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Application factory."""
    setup_logging()

    # Startup/Shutdown lifecycle
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        logger.info("Starting %s v%s", settings.app_name, settings.app_version)
        db = DatabaseManager()
        db.initialize()
        logger.info("DuckDB initialized at %s", settings.duckdb_path)
        
        # Start background cleanup task
        cleanup_task = asyncio.create_task(_cleanup_sessions_background())
        
        yield
        
        # Shutdown - Ensure proper cleanup
        logger.info("Shutting down %s", settings.app_name)
        
        # Cancel cleanup task
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
        
        # Close database connection
        try:
            db.close()
            logger.info("Database connection closed successfully")
        except Exception as e:
            logger.error("Error closing database: %s", e)
        
        # Small delay to ensure cleanup completes
        await asyncio.sleep(0.1)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered Excel data analysis platform. Upload workbooks, ask questions, generate charts and reports.",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Middleware - Exception handler MUST be registered first (outermost)
    app.add_middleware(ExceptionHandlingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include all API routes
    app.include_router(api_router)

    return app


async def _cleanup_sessions_background():
    """Background task to cleanup expired sessions every 5 minutes."""
    while True:
        try:
            await asyncio.sleep(300)  # 5 minutes
            count = SessionService.cleanup_expired_sessions()
            if count > 0:
                logger.debug("Session cleanup: removed %d expired sessions", count)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error("Error in session cleanup task: %s", e)


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )