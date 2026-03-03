"""Database configuration and session management."""

from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import settings

# Create engine based on database URL
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.is_sqlite else {},
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Get database session generator for FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables."""
    from app.models import Job, JobApplication  # noqa: F401

    Base.metadata.create_all(bind=engine)

    if settings.is_sqlite:
        # Enable foreign keys for SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()


def seed_database(db: Session) -> None:
    """Seed database with sample data if empty."""
    from app.models import Job
    from app.services.seed import get_seed_jobs

    # Check if jobs already exist
    existing_count = db.query(Job).count()
    if existing_count > 0:
        print(f"Database already has {existing_count} jobs, skipping seed.")
        return

    print("Seeding database with sample jobs...")
    seed_jobs = get_seed_jobs()

    for job_data in seed_jobs:
        db.add(Job(**job_data))

    db.commit()
    print(f"Added {len(seed_jobs)} sample jobs.")
