"""Shared dependencies for the job board application."""

from datetime import datetime

from fastapi import Request
from sqlalchemy.orm import Session

from app.config import settings
from app.services.crud import get_job_stats


def get_template_context(request: Request, db: Session, **kwargs) -> dict:
    """Build common template context."""
    context = {
        "request": request,
        "app_name": settings.MCP_SERVER_NAME,
        "current_year": datetime.utcnow().year,
    }

    # Add stats for sidebar
    stats = get_job_stats(db)
    context["total_jobs"] = stats.get("total_jobs", 0)
    context["total_applications"] = stats.get("total_applications", 0)
    context["companies_count"] = stats.get("companies_hiring", 0)

    context.update(kwargs)
    return context