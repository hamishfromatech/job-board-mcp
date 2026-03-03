"""FastMCP Job Board Server - Database-backed MCP server."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from app.config import settings
from app.database import SessionLocal, init_db, seed_database
from app.services.crud import (
    create_application,
    create_job,
    delete_job,
    get_application_by_id,
    get_applications,
    get_job_by_id,
    get_job_categories,
    get_job_stats,
    get_jobs,
    search_jobs as crud_search_jobs,
    update_job,
)

# Create FastMCP instance
mcp = FastMCP(
    name=settings.MCP_SERVER_NAME,
    instructions="A job board MCP server for finding and applying to jobs. Supports job search, applications, and management.",
    version="2.0.0",
)


# =============================================================================
# Helper function for DB session
# =============================================================================

def get_db_session():
    """Get a database session context manager."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =============================================================================
# MCP Tools
# =============================================================================

@mcp.tool
def get_jobs(
    location: Optional[str] = None,
    industry: Optional[str] = None,
    job_type: Optional[str] = None,
    remote_friendly: Optional[bool] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    Get available jobs with optional filtering.

    Args:
        location: Filter by location (e.g., "your city")
        industry: Filter by industry (e.g., "Technology", "Mining", "Healthcare")
        job_type: Filter by job type ("Full-time", "Part-time", "Contract", "Casual")
        remote_friendly: Filter for remote-friendly positions
        limit: Maximum number of jobs to return (default: 10)

    Returns:
        List of job dictionaries with basic information
    """
    db = next(get_db_session())
    try:
        jobs = get_jobs(
            db,
            location=location,
            industry=industry,
            job_type=job_type,
            remote_friendly=remote_friendly,
            limit=limit,
        )
        return [job.to_dict() for job in jobs]
    finally:
        db.close()


@mcp.tool
def search_jobs(keyword: str, limit: int = 5) -> Dict[str, Any]:
    """
    Search for jobs by keyword in title, company, description, or requirements.

    Args:
        keyword: Search keyword
        limit: Maximum number of results (default: 5)

    Returns:
        Dictionary with search results and metadata
    """
    if not keyword or not keyword.strip():
        return {"error": "Please provide a search keyword", "jobs": []}

    db = next(get_db_session())
    try:
        jobs = crud_search_jobs(db, keyword, limit=limit)
        job_list = [job.to_dict() for job in jobs]

        return {
            "search_term": keyword,
            "total_results": len(jobs),
            "showing_results": len(job_list),
            "jobs": job_list,
        }
    finally:
        db.close()


@mcp.tool
def get_job_details(job_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific job.

    Args:
        job_id: Unique job identifier (UUID)

    Returns:
        Complete job details or error message
    """
    db = next(get_db_session())
    try:
        job = get_job_by_id(db, job_id)

        if not job:
            return {"error": f"Job with ID '{job_id}' not found"}

        job_details = job.to_dict()

        # Add additional computed fields
        job_details["is_expired"] = (
            job.expiry_date < datetime.utcnow() if job.expiry_date else False
        )
        job_details["days_since_posted"] = (
            (datetime.utcnow() - job.posted_date).days if job.posted_date else None
        )

        return job_details
    finally:
        db.close()


@mcp.tool
def apply_for_job(
    job_id: str,
    applicant_name: str,
    applicant_email: str,
    applicant_phone: str = "",
    cover_letter: str = "",
    resume_link: str = "",
) -> Dict[str, Any]:
    """
    Apply for a specific job.

    Args:
        job_id: The job ID to apply for
        applicant_name: Full name of the applicant
        applicant_email: Email address for contact
        applicant_phone: Phone number for contact (optional)
        cover_letter: Cover letter text (optional)
        resume_link: Link to resume/PDF (optional)

    Returns:
        Application confirmation with application ID
    """
    # Validate inputs
    if not applicant_name or not applicant_name.strip():
        return {"error": "Applicant name is required"}

    if not applicant_email or not applicant_email.strip():
        return {"error": "Applicant email is required"}

    db = next(get_db_session())
    try:
        # Check if job exists
        job = get_job_by_id(db, job_id)
        if not job:
            return {"error": f"Job with ID '{job_id}' not found"}

        if not job.is_active:
            return {"error": "This job is no longer accepting applications"}

        # Submit application
        application_data = {
            "job_id": job_id,
            "applicant_name": applicant_name.strip(),
            "applicant_email": applicant_email.strip(),
            "applicant_phone": applicant_phone.strip() if applicant_phone else "",
            "cover_letter": cover_letter.strip() if cover_letter else "",
            "resume_link": resume_link.strip() if resume_link else "",
        }

        application = create_application(db, application_data)

        return {
            "success": True,
            "message": f"Application submitted successfully for {job.title} at {job.company}",
            "application_id": application.id,
            "job_details": {
                "title": job.title,
                "company": job.company,
                "location": job.location,
            },
            "application_status": application.status,
            "applied_date": application.applied_date.isoformat() if application.applied_date else None,
        }
    finally:
        db.close()


@mcp.tool
def get_job_categories() -> Dict[str, Any]:
    """
    Get available job categories, types, and filters.

    Returns:
        Dictionary with available filter options
    """
    db = next(get_db_session())
    try:
        categories = get_job_categories(db)

        return {
            "available_filters": categories,
            "location_focus": "your city and surrounding regions",
            "total_jobs_available": len(get_jobs(db, limit=10000)),
            "remote_jobs_count": len([job for job in get_jobs(db, limit=10000) if job.remote_friendly]),
        }
    finally:
        db.close()


@mcp.tool
def get_job_stats() -> Dict[str, Any]:
    """
    Get statistics about available jobs.

    Returns:
        Dictionary with job statistics
    """
    db = next(get_db_session())
    try:
        stats = get_job_stats(db)
        return stats
    finally:
        db.close()


@mcp.tool
def get_application_status(application_id: str) -> Dict[str, Any]:
    """
    Check the status of a job application.

    Args:
        application_id: The application ID returned when applying

    Returns:
        Application status and details
    """
    db = next(get_db_session())
    try:
        application = get_application_by_id(db, application_id)

        if not application:
            return {"error": f"Application with ID '{application_id}' not found"}

        return {
            "application_id": application.id,
            "status": application.status,
            "applied_date": application.applied_date.isoformat() if application.applied_date else None,
            "job_details": {
                "title": application.job.title,
                "company": application.job.company,
                "location": application.job.location,
            } if application.job else None,
            "applicant_name": application.applicant_name,
            "applicant_email": application.applicant_email,
        }
    finally:
        db.close()


# =============================================================================
# Admin Tools (Optional - for management via MCP)
# =============================================================================

@mcp.tool
def create_job_listing(
    title: str,
    company: str,
    location: str,
    job_type: str,
    industry: str,
    experience_level: str,
    description: str,
    salary_range: str = "",
    requirements: List[str] = None,
    benefits: List[str] = None,
    remote_friendly: bool = False,
) -> Dict[str, Any]:
    """
    Create a new job listing (admin tool).

    Args:
        title: Job title
        company: Company name
        location: Job location
        job_type: Job type (Full-time, Part-time, Contract, Casual)
        industry: Industry category
        experience_level: Experience level (Entry, Mid, Senior, Executive)
        description: Job description
        salary_range: Salary range text (optional)
        requirements: List of requirements (optional)
        benefits: List of benefits (optional)
        remote_friendly: Whether the job is remote-friendly

    Returns:
        Created job details
    """
    db = next(get_db_session())
    try:
        job_data = {
            "title": title,
            "company": company,
            "location": location,
            "job_type": job_type,
            "industry": industry,
            "experience_level": experience_level,
            "description": description,
            "salary_range": salary_range,
            "requirements": requirements or [],
            "benefits": benefits or [],
            "remote_friendly": remote_friendly,
        }

        job = create_job(db, job_data)

        return {
            "success": True,
            "message": "Job created successfully",
            "job": job.to_dict(),
        }
    finally:
        db.close()


@mcp.tool
def update_job_listing(
    job_id: str,
    title: Optional[str] = None,
    company: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    industry: Optional[str] = None,
    experience_level: Optional[str] = None,
    description: Optional[str] = None,
    salary_range: Optional[str] = None,
    remote_friendly: Optional[bool] = None,
    is_active: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Update an existing job listing (admin tool).

    Args:
        job_id: Job ID to update
        title: New title (optional)
        company: New company (optional)
        location: New location (optional)
        job_type: New job type (optional)
        industry: New industry (optional)
        experience_level: New experience level (optional)
        description: New description (optional)
        salary_range: New salary range (optional)
        remote_friendly: New remote-friendly status (optional)
        is_active: New active status (optional)

    Returns:
        Updated job details
    """
    db = next(get_db_session())
    try:
        job = get_job_by_id(db, job_id)
        if not job:
            return {"error": f"Job with ID '{job_id}' not found"}

        update_data = {}
        if title is not None:
            update_data["title"] = title
        if company is not None:
            update_data["company"] = company
        if location is not None:
            update_data["location"] = location
        if job_type is not None:
            update_data["job_type"] = job_type
        if industry is not None:
            update_data["industry"] = industry
        if experience_level is not None:
            update_data["experience_level"] = experience_level
        if description is not None:
            update_data["description"] = description
        if salary_range is not None:
            update_data["salary_range"] = salary_range
        if remote_friendly is not None:
            update_data["remote_friendly"] = remote_friendly
        if is_active is not None:
            update_data["is_active"] = is_active

        updated_job = update_job(db, job_id, update_data)

        return {
            "success": True,
            "message": "Job updated successfully",
            "job": updated_job.to_dict(),
        }
    finally:
        db.close()


@mcp.tool
def delete_job_listing(job_id: str) -> Dict[str, Any]:
    """
    Delete a job listing (admin tool).

    Args:
        job_id: Job ID to delete

    Returns:
        Deletion confirmation
    """
    db = next(get_db_session())
    try:
        success = delete_job(db, job_id)

        if not success:
            return {"error": f"Job with ID '{job_id}' not found"}

        return {
            "success": True,
            "message": "Job deleted successfully",
        }
    finally:
        db.close()


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Initialize and run the MCP server."""
    print("Initializing database...")
    init_db()

    # Seed data if enabled
    if settings.ENABLE_SEED_DATA:
        db = next(get_db_session())
        try:
            seed_database(db)
        finally:
            db.close()

    print(f"Starting {settings.MCP_SERVER_NAME}...")
    mcp.run()


if __name__ == "__main__":
    main()
