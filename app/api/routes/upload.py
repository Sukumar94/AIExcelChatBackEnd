"""
File upload routes - single and multi-file upload.
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status

from app.api.dependencies import get_upload_service
from app.schemas.upload import MultiUploadResponse, UploadResponse
from app.services.upload_service import UploadService

router = APIRouter(
    prefix="/api/v1/upload",
    tags=["Upload"],
)


@router.post("", response_model=UploadResponse)
async def upload_excel(
    file: UploadFile = File(...),
    upload_service: UploadService = Depends(get_upload_service),
):
    """Upload a single Excel workbook."""
    try:
        result = await upload_service.upload(file)
        return UploadResponse(
            success=True,
            session_id=result["session_id"],
            file_name=result["file_name"],
            file_size=result["file_size"],
            sheet_count=result["sheet_count"],
            sheets=result["sheets"],
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file: {str(e)}",
        )
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File is too large or corrupted",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Upload failed. Please try again.",
        )


@router.post("/multiple", response_model=MultiUploadResponse)
async def upload_multiple_excel(
    files: List[UploadFile] = File(...),
    upload_service: UploadService = Depends(get_upload_service),
):
    """Upload multiple Excel workbooks at once."""
    try:
        results = await upload_service.upload_multiple(files)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch upload failed. Please try again.",
        )
    responses = []
    for r in results:
        if r.get("session_id"):
            responses.append(UploadResponse(
                success=True,
                session_id=r["session_id"],
                file_name=r["file_name"],
                file_size=r.get("file_size", 0),
                sheet_count=r.get("sheet_count", 0),
                sheets=r.get("sheets", []),
            ))
        else:
            responses.append(UploadResponse(
                success=False,
                session_id="",
                file_name=r.get("file_name", "unknown"),
                file_size=0,
                sheet_count=0,
                message=r.get("error", "Upload failed"),
            ))
    return MultiUploadResponse(
        success=True,
        sessions=responses,
        total_files=len(files),
    )