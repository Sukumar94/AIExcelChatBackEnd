"""
Custom exception classes for the application.
"""

from typing import Any


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = 500, detail: Any = None) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        super().__init__(self.message)


class WorkbookNotFoundError(AppException):
    """Raised when a workbook session is not found."""

    def __init__(self, session_id: str) -> None:
        super().__init__(
            message=f"Workbook session {session_id} not found.",
            status_code=404,
            detail=f"Session '{session_id}' does not exist or has expired.",
        )


class SheetNotFoundError(AppException):
    """Raised when a sheet is not found in the workbook."""

    def __init__(self, session_id: str, sheet_name: str) -> None:
        super().__init__(
            message=f"Sheet '{sheet_name}' not found in session {session_id}.",
            status_code=404,
            detail=f"The workbook does not contain a sheet named '{sheet_name}'.",
        )


class FileValidationError(AppException):
    """Raised when file validation fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(
            message="File validation failed.",
            status_code=400,
            detail=detail,
        )


class QueryExecutionError(AppException):
    """Raised when a SQL query against the workbook fails."""

    def __init__(self, original_error: str) -> None:
        super().__init__(
            message="Failed to execute query.",
            status_code=400,
            detail=f"Query execution error: {original_error}",
        )


class LLMServiceError(AppException):
    """Raised when the LLM service is unavailable or returns an error."""

    def __init__(self, detail: str = "LLM service unavailable.") -> None:
        super().__init__(
            message="LLM service error.",
            status_code=503,
            detail=detail,
        )


class ChartGenerationError(AppException):
    """Raised when chart generation fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(
            message="Chart generation failed.",
            status_code=500,
            detail=detail,
        )


class ExportError(AppException):
    """Raised when export fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(
            message="Export failed.",
            status_code=500,
            detail=detail,
        )


class ValidationError(AppException):
    """Raised when input validation fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(
            message="Validation failed.",
            status_code=400,
            detail=detail,
        )