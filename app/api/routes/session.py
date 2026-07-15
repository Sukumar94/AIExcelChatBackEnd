"""
Session management routes.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.services.session_service import SessionService

router = APIRouter(
    prefix="/api/v1/sessions",
    tags=["Sessions"],
)


@router.get("/{session_id}")
async def get_session(session_id: str):
    """Get session details."""
    session = SessionService.get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return {
        "session_id": session.session_id,
        "file_name": session.metadata.file_name,
        "file_size": session.metadata.file_size,
        "total_sheets": session.metadata.total_sheets,
        "uploaded_at": str(session.metadata.uploaded_at),
        "sheets": [
            {
                "name": s.sheet_name,
                "rows": s.rows,
                "columns": s.columns,
                "column_names": s.column_names,
            }
            for s in session.sheets.values()
        ],
    }


@router.get("/{session_id}/preview/{sheet_name}")
async def preview_sheet(session_id: str, sheet_name: str, limit: int = 100):
    """Preview data from a specific sheet."""
    session = SessionService.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if sheet_name not in session.sheets:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Sheet '{sheet_name}' not found")

    df = session.sheets[sheet_name].dataframe.head(limit)
    return {
        "sheet_name": sheet_name,
        "columns": df.columns,
        "rows": df.head(limit).to_dicts(),
    }


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    deleted = SessionService.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return {"success": True, "message": "Session deleted"}