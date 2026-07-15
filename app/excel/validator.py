"""
Excel file validation.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.constants import ALLOWED_EXTENSIONS, MAX_FILE_SIZE


class ExcelValidator:
    """Validates uploaded Excel files."""

    @staticmethod
    async def validate(file: UploadFile) -> None:
        """
        Validate the uploaded file.
        Raises HTTPException on validation failure.
        """
        if file is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file uploaded.",
            )

        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is missing.",
            )

        extension = Path(file.filename).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Unsupported file type '{extension}'. "
                    f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
                ),
            )

        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds the maximum allowed size ({MAX_FILE_SIZE // (1024*1024)} MB).",
            )

        await file.seek(0)