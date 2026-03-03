"""FastAPI web server with dashboard for job board management."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import get_db, init_db, seed_database
from app.routers import pages_router, jobs_router, applications_router, ai_router

# Create FastAPI app
app = FastAPI(
    title="Job Board Dashboard",
    description="Web dashboard for managing job board",
    version="2.0.0",
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# =============================================================================
# Include Routers
# =============================================================================

app.include_router(pages_router)
app.include_router(jobs_router)
app.include_router(applications_router)
app.include_router(ai_router)


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Initialize and run the web server."""
    print("Initializing database...")
    init_db()

    # Seed data if enabled
    if settings.ENABLE_SEED_DATA:
        db = next(get_db())
        seed_database(db)

    print(f"Starting web server on http://{settings.WEB_HOST}:{settings.WEB_PORT}")
    import uvicorn
    uvicorn.run(
        "app.web_server:app",
        host=settings.WEB_HOST,
        port=settings.WEB_PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    main()