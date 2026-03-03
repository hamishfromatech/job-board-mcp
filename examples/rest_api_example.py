#!/usr/bin/env python3
"""
Example: Using the REST API

This script demonstrates how to interact with the web dashboard's REST API programmatically.

Usage:
    1. Start the web server: python -m app.web_server
    2. In another terminal, run: python examples/rest_api_example.py
"""

import httpx
import json


BASE_URL = "http://localhost:8000/api"


def get_jobs():
    """Get all jobs via REST API."""
    response = httpx.get(f"{BASE_URL}/jobs")
    if response.status_code == 200:
        return response.json()
    return None


def create_job(job_data):
    """Create a job via REST API."""
    response = httpx.post(f"{BASE_URL}/jobs", data=job_data)
    return response


def main():
    """Run the REST API examples."""

    print("=" * 60)
    print("Job Board REST API Examples")
    print("=" * 60)

    # Get all jobs
    print("\n1. Getting all jobs...")
    jobs = get_jobs()
    if jobs:
        print(f"   Found {len(jobs)} jobs")
    else:
        print("   Failed to get jobs or server not running")

    # Create a new job
    print("\n2. Creating a new job...")
    new_job = {
        "title": "DevOps Engineer",
        "company": "Cloud Solutions Inc",
        "location": "Mackay, QLD",
        "job_type": "Full-time",
        "industry": "Technology",
        "experience_level": "Mid",
        "description": "Join our DevOps team to build and maintain cloud infrastructure.",
        "salary_range": "$80,000 - $100,000 AUD",
        "requirements": "Experience with Docker and Kubernetes\nKnowledge of AWS or Azure\nStrong scripting skills (Python/Bash)",
        "benefits": "Remote work options\nProfessional development\nTeam events",
        "remote_friendly": "true",
    }

    try:
        response = create_job(new_job)
        if response.status_code in [200, 201, 302]:
            print("   Job created successfully!")
        else:
            print(f"   Response: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
        print("   Note: Make sure the web server is running on localhost:8000")

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
