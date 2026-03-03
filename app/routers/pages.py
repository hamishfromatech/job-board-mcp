"""Page routes for HTML responses."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_template_context
from app.models import JobApplication
from app.services.crud import (
    get_applications,
    get_job_by_id,
    get_job_categories,
    get_job_stats,
    get_jobs,
    search_jobs,
)

router = APIRouter(tags=["pages"])


# =============================================================================
# Dashboard
# =============================================================================

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Main dashboard page."""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")

    stats = get_job_stats(db)
    recent_jobs = get_jobs(db, limit=5)
    recent_applications = get_applications(db, limit=5)

    context = get_template_context(
        request, db,
        stats=stats,
        recent_jobs=recent_jobs,
        recent_applications=recent_applications,
    )
    return templates.TemplateResponse("dashboard.html", context)


# =============================================================================
# Jobs Pages
# =============================================================================

@router.get("/jobs", response_class=HTMLResponse)
async def jobs_list(
    request: Request,
    db: Session = Depends(get_db),
    search: Optional[str] = None,
    industry: Optional[str] = None,
    job_type: Optional[str] = None,
    remote: Optional[bool] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """Jobs listing page with search and filters."""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")

    skip = (page - 1) * per_page

    if search:
        jobs_result = search_jobs(db, search, limit=per_page)
    else:
        jobs_result = get_jobs(
            db, skip=skip, limit=per_page,
            industry=industry,
            job_type=job_type,
            remote_friendly=remote,
        )

    categories = get_job_categories(db)

    context = get_template_context(
        request, db,
        jobs=jobs_result,
        categories=categories,
        search=search,
        industry=industry,
        job_type=job_type,
        remote=remote,
        page=page,
        per_page=per_page,
    )
    return templates.TemplateResponse("jobs.html", context)


@router.get("/jobs/new", response_class=HTMLResponse)
async def new_job_form(request: Request, db: Session = Depends(get_db)):
    """Form for creating a new job."""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    from app.config import settings

    categories = get_job_categories(db)
    context = get_template_context(
        request, db,
        categories=categories,
        default_location=settings.DEFAULT_LOCATION,
    )
    return templates.TemplateResponse("job_form.html", context)


@router.get("/jobs/{job_id}/edit", response_class=HTMLResponse)
async def edit_job_form(request: Request, job_id: str, db: Session = Depends(get_db)):
    """Form for editing a job."""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")

    job = get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    categories = get_job_categories(db)
    context = get_template_context(
        request, db,
        job=job,
        categories=categories,
        edit_mode=True,
    )
    return templates.TemplateResponse("job_form.html", context)


@router.get("/jobs/{job_id}", response_class=HTMLResponse)
async def job_detail(request: Request, job_id: str, db: Session = Depends(get_db)):
    """Job detail page."""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")

    job = get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job_applications = get_applications(db, job_id=job_id)

    context = get_template_context(
        request, db,
        job=job,
        applications=job_applications,
    )
    return templates.TemplateResponse("job_detail.html", context)


# =============================================================================
# Applications Pages
# =============================================================================

@router.get("/applications", response_class=HTMLResponse)
async def applications_list(
    request: Request,
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """Applications listing page."""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")

    skip = (page - 1) * per_page

    applications = get_applications(db, skip=skip, limit=per_page, status=status)

    context = get_template_context(
        request, db,
        applications=applications,
        status=status,
        page=page,
        per_page=per_page,
    )
    return templates.TemplateResponse("applications.html", context)


@router.get("/applications/{application_id}", response_class=HTMLResponse)
async def application_detail(
    request: Request,
    application_id: str,
    db: Session = Depends(get_db),
):
    """Application detail page."""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")

    application = db.query(JobApplication).filter(
        JobApplication.id == application_id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    context = get_template_context(
        request, db,
        application=application,
    )
    return templates.TemplateResponse("application_detail.html", context)


# =============================================================================
# Statistics Page
# =============================================================================

@router.get("/statistics", response_class=HTMLResponse)
async def statistics(request: Request, db: Session = Depends(get_db)):
    """Statistics page."""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")

    stats = get_job_stats(db)
    categories = get_job_categories(db)

    context = get_template_context(
        request, db,
        stats=stats,
        categories=categories,
    )
    return templates.TemplateResponse("statistics.html", context)