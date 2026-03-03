"""SQLAlchemy models for job board."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


def generate_uuid():
    """Generate a unique identifier."""
    return str(uuid.uuid4())


class Job(Base):
    """Job listing model."""

    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(200), nullable=False, index=True)
    company = Column(String(200), nullable=False, index=True)
    location = Column(String(200), nullable=False, default="Mackay, QLD")
    job_type = Column(String(50), nullable=False)  # Full-time, Part-time, Contract, Casual
    salary_range = Column(String(100))
    description = Column(Text, nullable=False)
    requirements = Column(Text)  # JSON list stored as text
    benefits = Column(Text)  # JSON list stored as text
    posted_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime)
    industry = Column(String(100), index=True)
    experience_level = Column(String(50))  # Entry, Mid, Senior, Executive
    remote_friendly = Column(Boolean, default=False)
    applications_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    applications = relationship("JobApplication", back_populates="job", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        import json

        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "job_type": self.job_type,
            "salary_range": self.salary_range,
            "description": self.description,
            "requirements": json.loads(self.requirements) if self.requirements else [],
            "benefits": json.loads(self.benefits) if self.benefits else [],
            "posted_date": self.posted_date.isoformat() if self.posted_date else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "industry": self.industry,
            "experience_level": self.experience_level,
            "remote_friendly": self.remote_friendly,
            "applications_count": self.applications_count,
            "is_active": self.is_active,
        }


class JobApplication(Base):
    """Job application model."""

    __tablename__ = "job_applications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)
    applicant_name = Column(String(200), nullable=False)
    applicant_email = Column(String(200), nullable=False, index=True)
    applicant_phone = Column(String(50))
    cover_letter = Column(Text)
    resume_link = Column(String(500))
    applied_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="pending")  # pending, reviewing, interviewing, offered, rejected
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="applications")

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "job_id": self.job_id,
            "applicant_name": self.applicant_name,
            "applicant_email": self.applicant_email,
            "applicant_phone": self.applicant_phone,
            "cover_letter": self.cover_letter,
            "resume_link": self.resume_link,
            "applied_date": self.applied_date.isoformat() if self.applied_date else None,
            "status": self.status,
            "notes": self.notes,
        }
