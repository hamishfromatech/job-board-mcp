"""Job API routes."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.crud import create_job, delete_job, toggle_job_active, update_job

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("")
async def create_job_endpoint(
    title: str = Form(...),
    company: str = Form(...),
    location: str = Form(...),
    job_type: str = Form(...),
    industry: str = Form(...),
    experience_level: str = Form("Entry"),
    salary_range: str = Form(""),
    description: str = Form(...),
    requirements: str = Form(""),
    benefits: str = Form(""),
    remote_friendly: bool = Form(False),
    expiry_date: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """API endpoint to create a new job."""
    job_data = {
        "title": title,
        "company": company,
        "location": location,
        "job_type": job_type,
        "industry": industry,
        "experience_level": experience_level,
        "salary_range": salary_range,
        "description": description,
        "requirements": [r.strip() for r in requirements.split("\n") if r.strip()],
        "benefits": [b.strip() for b in benefits.split("\n") if b.strip()],
        "remote_friendly": remote_friendly,
    }

    if expiry_date:
        try:
            job_data["expiry_date"] = datetime.fromisoformat(expiry_date)
        except ValueError:
            pass

    job = create_job(db, job_data)
    return RedirectResponse(url=f"/jobs/{job.id}", status_code=status.HTTP_302_FOUND)


@router.post("/{job_id}/update")
async def update_job_endpoint(
    job_id: str,
    title: str = Form(...),
    company: str = Form(...),
    location: str = Form(...),
    job_type: str = Form(...),
    industry: str = Form(...),
    experience_level: str = Form(...),
    salary_range: str = Form(""),
    description: str = Form(...),
    requirements: str = Form(""),
    benefits: str = Form(""),
    remote_friendly: bool = Form(False),
    expiry_date: Optional[str] = Form(None),
    is_active: bool = Form(True),
    db: Session = Depends(get_db),
):
    """API endpoint to update a job."""
    job_data = {
        "title": title,
        "company": company,
        "location": location,
        "job_type": job_type,
        "industry": industry,
        "experience_level": experience_level,
        "salary_range": salary_range,
        "description": description,
        "requirements": [r.strip() for r in requirements.split("\n") if r.strip()],
        "benefits": [b.strip() for b in benefits.split("\n") if b.strip()],
        "remote_friendly": remote_friendly,
        "is_active": is_active,
    }

    if expiry_date:
        try:
            job_data["expiry_date"] = datetime.fromisoformat(expiry_date)
        except ValueError:
            pass

    job = update_job(db, job_id, job_data)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return RedirectResponse(url=f"/jobs/{job_id}", status_code=status.HTTP_302_FOUND)


@router.post("/{job_id}/delete")
async def delete_job_endpoint(job_id: str, db: Session = Depends(get_db)):
    """API endpoint to delete a job."""
    success = delete_job(db, job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return RedirectResponse(url="/jobs", status_code=status.HTTP_302_FOUND)


@router.post("/{job_id}/toggle")
async def toggle_job_endpoint(job_id: str, db: Session = Depends(get_db)):
    """API endpoint to toggle job active status."""
    job = toggle_job_active(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return RedirectResponse(url=f"/jobs/{job_id}", status_code=status.HTTP_302_FOUND)