"""CRUD operations for job board."""

import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models import Job, JobApplication


# =============================================================================
# Job CRUD Operations
# =============================================================================


def get_jobs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    location: Optional[str] = None,
    industry: Optional[str] = None,
    job_type: Optional[str] = None,
    remote_friendly: Optional[bool] = None,
    is_active: bool = True,
) -> List[Job]:
    """Get jobs with optional filtering."""
    query = db.query(Job)

    if is_active is not None:
        query = query.filter(Job.is_active == is_active)

    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    if industry:
        query = query.filter(func.lower(Job.industry) == industry.lower())

    if job_type:
        query = query.filter(func.lower(Job.job_type) == job_type.lower())

    if remote_friendly is not None:
        query = query.filter(Job.remote_friendly == remote_friendly)

    return query.order_by(desc(Job.posted_date)).offset(skip).limit(limit).all()


def search_jobs(db: Session, keyword: str, limit: int = 20) -> List[Job]:
    """Search jobs by keyword."""
    keyword_lower = keyword.lower()

    query = db.query(Job).filter(
        (func.lower(Job.title).contains(keyword_lower)) |
        (func.lower(Job.company).contains(keyword_lower)) |
        (func.lower(Job.description).contains(keyword_lower)) |
        (func.lower(Job.industry).contains(keyword_lower))
    )

    return query.filter(Job.is_active == True).limit(limit).all()


def get_job_by_id(db: Session, job_id: str) -> Optional[Job]:
    """Get a specific job by ID."""
    return db.query(Job).filter(Job.id == job_id).first()


def create_job(db: Session, job_data: dict) -> Job:
    """Create a new job."""
    # Convert lists to JSON strings
    if "requirements" in job_data and isinstance(job_data["requirements"], list):
        job_data["requirements"] = json.dumps(job_data["requirements"])
    if "benefits" in job_data and isinstance(job_data["benefits"], list):
        job_data["benefits"] = json.dumps(job_data["benefits"])

    # Set defaults
    job_data.setdefault("posted_date", datetime.utcnow())
    job_data.setdefault("is_active", True)

    db_job = Job(**job_data)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def update_job(db: Session, job_id: str, job_data: dict) -> Optional[Job]:
    """Update an existing job."""
    job = get_job_by_id(db, job_id)
    if not job:
        return None

    # Convert lists to JSON strings
    if "requirements" in job_data and isinstance(job_data["requirements"], list):
        job_data["requirements"] = json.dumps(job_data["requirements"])
    if "benefits" in job_data and isinstance(job_data["benefits"], list):
        job_data["benefits"] = json.dumps(job_data["benefits"])

    for key, value in job_data.items():
        setattr(job, key, value)

    job.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    return job


def delete_job(db: Session, job_id: str) -> bool:
    """Delete a job (soft delete by marking inactive or hard delete)."""
    job = get_job_by_id(db, job_id)
    if not job:
        return False

    db.delete(job)
    db.commit()
    return True


def toggle_job_active(db: Session, job_id: str) -> Optional[Job]:
    """Toggle job active status."""
    job = get_job_by_id(db, job_id)
    if not job:
        return None

    job.is_active = not job.is_active
    db.commit()
    db.refresh(job)
    return job


def get_job_categories(db: Session) -> dict:
    """Get available job categories."""
    industries = [row[0] for row in db.query(Job.industry).distinct().all() if row[0]]
    job_types = [row[0] for row in db.query(Job.job_type).distinct().all() if row[0]]
    experience_levels = [row[0] for row in db.query(Job.experience_level).distinct().all() if row[0]]
    locations = [row[0] for row in db.query(Job.location).distinct().all() if row[0]]

    return {
        "industries": sorted(industries),
        "job_types": sorted(job_types),
        "experience_levels": sorted(experience_levels),
        "locations": sorted(locations),
    }


def get_job_stats(db: Session) -> dict:
    """Get job statistics."""
    total_jobs = db.query(Job).filter(Job.is_active == True).count()
    total_applications = db.query(func.sum(Job.applications_count)).scalar() or 0

    # By industry
    industry_counts = db.query(Job.industry, func.count(Job.id)).filter(
        Job.is_active == True
    ).group_by(Job.industry).all()

    # By job type
    type_counts = db.query(Job.job_type, func.count(Job.id)).filter(
        Job.is_active == True
    ).group_by(Job.job_type).all()

    # By experience level
    exp_counts = db.query(Job.experience_level, func.count(Job.id)).filter(
        Job.is_active == True
    ).group_by(Job.experience_level).all()

    remote_count = db.query(Job).filter(
        Job.is_active == True,
        Job.remote_friendly == True
    ).count()

    companies_count = db.query(func.count(func.distinct(Job.company))).filter(
        Job.is_active == True
    ).scalar()

    # Recent jobs (last 7 days)
    recent_date = datetime.utcnow() - __import__('datetime').timedelta(days=7)
    recent_count = db.query(Job).filter(
        Job.is_active == True,
        Job.posted_date >= recent_date
    ).count()

    return {
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "companies_hiring": companies_count,
        "remote_jobs": remote_count,
        "recently_posted": recent_count,
        "jobs_by_industry": {industry: count for industry, count in industry_counts},
        "jobs_by_type": {job_type: count for job_type, count in type_counts},
        "jobs_by_experience": {level: count for level, count in exp_counts},
    }


# =============================================================================
# Application CRUD Operations
# =============================================================================


def get_applications(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    job_id: Optional[str] = None,
    status: Optional[str] = None,
) -> List[JobApplication]:
    """Get job applications with optional filtering."""
    query = db.query(JobApplication)

    if job_id:
        query = query.filter(JobApplication.job_id == job_id)

    if status:
        query = query.filter(func.lower(JobApplication.status) == status.lower())

    return query.order_by(desc(JobApplication.applied_date)).offset(skip).limit(limit).all()


def get_application_by_id(db: Session, application_id: str) -> Optional[JobApplication]:
    """Get a specific application by ID."""
    return db.query(JobApplication).filter(JobApplication.id == application_id).first()


def create_application(db: Session, application_data: dict) -> JobApplication:
    """Create a new job application."""
    # Create the application
    db_application = JobApplication(**application_data)
    db.add(db_application)

    # Increment job application count
    job = get_job_by_id(db, application_data["job_id"])
    if job:
        job.applications_count = (job.applications_count or 0) + 1

    db.commit()
    db.refresh(db_application)
    return db_application


def update_application_status(
    db: Session,
    application_id: str,
    status: str,
    notes: Optional[str] = None
) -> Optional[JobApplication]:
    """Update application status."""
    application = get_application_by_id(db, application_id)
    if not application:
        return None

    application.status = status
    if notes is not None:
        application.notes = notes
    application.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(application)
    return application


def delete_application(db: Session, application_id: str) -> bool:
    """Delete an application."""
    application = get_application_by_id(db, application_id)
    if not application:
        return False

    db.delete(application)
    db.commit()
    return True


def get_application_stats(db: Session) -> dict:
    """Get application statistics."""
    total = db.query(JobApplication).count()

    status_counts = db.query(
        JobApplication.status,
        func.count(JobApplication.id)
    ).group_by(JobApplication.status).all()

    recent_date = datetime.utcnow() - __import__('datetime').timedelta(days=7)
    recent_count = db.query(JobApplication).filter(
        JobApplication.applied_date >= recent_date
    ).count()

    return {
        "total_applications": total,
        "by_status": {status: count for status, count in status_counts},
        "recent_applications": recent_count,
    }
