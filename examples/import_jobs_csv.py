#!/usr/bin/env python3
"""
Example: Import Jobs from CSV

This script demonstrates how to import job listings from a CSV file.
Expected CSV format:
    title,company,location,job_type,industry,experience_level,description,salary_range,remote_friendly

Usage:
    python examples/import_jobs_csv.py jobs.csv
"""

import csv
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, init_db
from app.services.crud import create_job


def import_jobs_from_csv(csv_file_path):
    """Import jobs from a CSV file."""

    # Initialize database
    init_db()

    db = SessionLocal()
    try:
        imported = 0
        errors = 0

        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    # Parse requirements and benefits (semicolon separated)
                    requirements = []
                    benefits = []

                    if 'requirements' in row and row['requirements']:
                        requirements = [r.strip() for r in row['requirements'].split(';') if r.strip()]

                    if 'benefits' in row and row['benefits']:
                        benefits = [b.strip() for b in row['benefits'].split(';') if b.strip()]

                    job_data = {
                        "title": row.get('title', ''),
                        "company": row.get('company', ''),
                        "location": row.get('location', ''),
                        "job_type": row.get('job_type', 'Full-time'),
                        "industry": row.get('industry', ''),
                        "experience_level": row.get('experience_level', 'Entry'),
                        "description": row.get('description', ''),
                        "salary_range": row.get('salary_range', ''),
                        "requirements": requirements,
                        "benefits": benefits,
                        "remote_friendly": row.get('remote_friendly', '').lower() == 'true',
                    }

                    create_job(db, job_data)
                    imported += 1
                    print(f"  Imported: {job_data['title']}")

                except Exception as e:
                    print(f"  Error importing row: {e}")
                    errors += 1

        print(f"\nImport complete: {imported} jobs imported, {errors} errors")

    finally:
        db.close()


def create_sample_csv():
    """Create a sample CSV file for reference."""
    sample_data = """title,company,location,job_type,industry,experience_level,description,salary_range,remote_friendly
Software Engineer,Tech Corp,Mackay QLD,Full-time,Technology,Mid,Exciting software engineering role,$70000 - $90000,true
Marketing Manager,Marketing Agency,Mackay QLD,Full-time,Marketing,Senior,Lead marketing campaigns,$80000 - $100000,false
"""
    sample_path = Path("jobs_sample.csv")
    with open(sample_path, 'w') as f:
        f.write(sample_data)
    print(f"Sample CSV created: {sample_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_jobs_csv.py <csv_file>")
        print("       python import_jobs_csv.py --sample (creates a sample CSV)")
        sys.exit(1)

    if sys.argv[1] == "--sample":
        create_sample_csv()
    else:
        import_jobs_from_csv(sys.argv[1])
