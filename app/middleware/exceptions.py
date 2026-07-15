"""
Global exception handling middleware.
"""

from __future__ import annotations

import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    """Catches AppException and returns structured error responses."""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except AppException as e:
            logger.warning("AppException: %s", e.message)
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail, "status_code": e.status_code},
            )
        except Exception as e:
            logger.exception("Unhandled exception")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error.", "status_code": 500},
            )