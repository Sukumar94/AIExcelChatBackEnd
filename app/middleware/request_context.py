"""
Request context middleware for storing request-scoped data.
"""

from __future__ import annotations

import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """Get the current request ID."""
    return request_id_var.get()


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Sets a unique request ID for each request."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request_id_var.set(request_id)
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response