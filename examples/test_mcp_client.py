#!/usr/bin/env python3
"""
Example MCP Client for Job Board Server

This script demonstrates how to connect to and interact with the FastMCP job board server.
Run this while the MCP server is running to test the functionality.

Usage:
    1. Start the MCP server: python -m app.mcp_server
    2. In another terminal, run: python examples/test_mcp_client.py
"""

import asyncio
import json

from fastmcp import Client


async def test_job_board():
    """Test the job board MCP server."""

    print("=" * 60)
    print("Job Board MCP Client Test")
    print("=" * 60)

    # Connect to the MCP server
    async with Client("app.mcp_server:mcp") as client:

        # Test 1: Get all jobs
        print("\n1. Getting all jobs...")
        result = await client.call_tool("get_jobs", {"limit": 5})
        jobs = json.loads(result.content[0].text)
        print(f"   Found {len(jobs)} jobs")
        for job in jobs[:3]:
            print(f"   - {job['title']} at {job['company']}")

        # Test 2: Search for jobs
        print("\n2. Searching for 'software' jobs...")
        result = await client.call_tool("search_jobs", {"keyword": "software", "limit": 3})
        search_result = json.loads(result.content[0].text)
        print(f"   Found {search_result.get('total_results', 0)} matching jobs")

        # Test 3: Get job categories
        print("\n3. Getting job categories...")
        result = await client.call_tool("get_job_categories", {})
        categories = json.loads(result.content[0].text)
        print(f"   Industries: {', '.join(categories['available_filters']['industries'][:5])}")

        # Test 4: Get statistics
        print("\n4. Getting job statistics...")
        result = await client.call_tool("get_job_stats", {})
        stats = json.loads(result.content[0].text)
        print(f"   Total jobs: {stats.get('total_jobs', 0)}")
        print(f"   Total applications: {stats.get('total_applications', 0)}")

        # Test 5: Get remote jobs
        print("\n5. Getting remote-friendly jobs...")
        result = await client.call_tool("get_jobs", {"remote_friendly": True, "limit": 3})
        remote_jobs = json.loads(result.content[0].text)
        print(f"   Found {len(remote_jobs)} remote jobs")

        # Test 6: Get jobs by industry
        print("\n6. Getting Technology jobs...")
        result = await client.call_tool("get_jobs", {"industry": "Technology", "limit": 3})
        tech_jobs = json.loads(result.content[0].text)
        print(f"   Found {len(tech_jobs)} technology jobs")

        # Test 7: Submit an application (if there are jobs)
        if jobs:
            job_id = jobs[0]['id']
            print(f"\n7. Submitting application to job '{jobs[0]['title']}'...")
            result = await client.call_tool(
                "apply_for_job",
                {
                    "job_id": job_id,
                    "applicant_name": "Test Candidate",
                    "applicant_email": "test@example.com",
                    "applicant_phone": "+61 412 345 678",
                    "cover_letter": "This is a test application submitted via the MCP client.",
                    "resume_link": "https://example.com/resume.pdf",
                }
            )
            application_result = json.loads(result.content[0].text)
            if "error" in application_result:
                print(f"   Error: {application_result['error']}")
            else:
                print(f"   Application submitted! ID: {application_result.get('application_id')}")

        print("\n" + "=" * 60)
        print("Test completed!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_job_board())
