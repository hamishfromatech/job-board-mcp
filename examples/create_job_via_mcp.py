#!/usr/bin/env python3
"""
Example: Create a Job via MCP

This script demonstrates creating a job using the MCP admin tools.

Usage:
    1. Start the MCP server: python -m app.mcp_server
    2. In another terminal, run: python examples/create_job_via_mcp.py
"""

import asyncio
import json

from fastmcp import Client


async def create_job():
    """Create a new job via MCP."""

    print("Creating new job via MCP...")

    async with Client("app.mcp_server:mcp") as client:
        result = await client.call_tool(
            "create_job_listing",
            {
                "title": "Senior Python Developer",
                "company": "Tech Innovations Pty Ltd",
                "location": "Mackay, QLD",
                "job_type": "Full-time",
                "industry": "Technology",
                "experience_level": "Senior",
                "description": """We are looking for an experienced Python Developer to join our growing team.

Key responsibilities:
- Design and develop scalable backend systems
- Work with modern Python frameworks (FastAPI, Django)
- Collaborate with frontend developers and product managers
- Write clean, maintainable, and tested code

This is an exciting opportunity to work on cutting-edge projects in the Mackay region.""",
                "salary_range": "$90,000 - $120,000 AUD",
                "requirements": [
                    "5+ years of Python development experience",
                    "Experience with FastAPI or Django",
                    "Strong understanding of SQL databases",
                    "Experience with cloud platforms (AWS/Azure)",
                    "Excellent problem-solving skills",
                    "Strong communication skills"
                ],
                "benefits": [
                    "Competitive salary package",
                    "Flexible working arrangements",
                    "Professional development budget",
                    "Health and wellness program",
                    "Modern office in Mackay CBD"
                ],
                "remote_friendly": True,
            }
        )

        response = json.loads(result.content[0].text)
        print(json.dumps(response, indent=2))

        if "success" in response:
            print(f"\nJob created successfully!")
            print(f"Job ID: {response['job']['id']}")
            print(f"Title: {response['job']['title']}")
        else:
            print(f"\nError: {response.get('error', 'Unknown error')}")


if __name__ == "__main__":
    asyncio.run(create_job())
