"""FastAPI routers for the job board application."""

from app.routers.pages import router as pages_router
from app.routers.jobs import router as jobs_router
from app.routers.applications import router as applications_router
from app.routers.ai import router as ai_router

__all__ = ["pages_router", "jobs_router", "applications_router", "ai_router"]