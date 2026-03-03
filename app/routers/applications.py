"""Application API routes."""

from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.crud import update_application_status

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.post("/{application_id}/status")
async def update_status_endpoint(
    application_id: str,
    status: str = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """API endpoint to update application status."""
    application = update_application_status(db, application_id, status, notes)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return RedirectResponse(
        url=f"/applications/{application_id}",
        status_code=status.HTTP_302_FOUND
    )