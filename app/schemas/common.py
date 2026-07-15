"""
Common/shared Pydantic schemas.
"""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
    status_code: int = 500


class SuccessResponse(BaseModel):
    """Standard success response."""

    success: bool = True
    message: str = "Operation completed successfully."