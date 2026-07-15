"""
Authentication middleware (placeholder for future API key validation).
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Optional authentication middleware. Currently permits all requests."""

    async def dispatch(self, request: Request, call_next):
        # Future: validate API key / JWT token here
        response: Response = await call_next(request)
        return response