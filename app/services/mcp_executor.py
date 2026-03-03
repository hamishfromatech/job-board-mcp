"""MCP Tool Executor for AI Assistant."""

from typing import Any, Dict

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.crud import (
    create_job,
    get_job_by_id,
    get_job_categories,
    get_job_stats,
    get_jobs,
    search_jobs,
)


class MCPToolExecutor:
    """Executes MCP tools for the AI Assistant."""

    def __init__(self):
        self.db: Session = SessionLocal()

    def close(self):
        """Close database session."""
        self.db.close()

    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute an MCP tool by name with arguments."""
        try:
            if tool_name == "get_jobs":
                return await self._get_jobs(arguments)
            elif tool_name == "search_jobs":
                return await self._search_jobs(arguments)
            elif tool_name == "get_job_details":
                return await self._get_job_details(arguments)
            elif tool_name == "get_job_categories":
                return await self._get_job_categories(arguments)
            elif tool_name == "get_job_stats":
                return await self._get_job_stats(arguments)
            elif tool_name == "create_job_listing":
                return await self._create_job_listing(arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _get_jobs(self, arguments: Dict) -> Dict:
        """Execute get_jobs tool."""
        jobs = get_jobs(
            self.db,
            location=arguments.get("location"),
            industry=arguments.get("industry"),
            job_type=arguments.get("job_type"),
            remote_friendly=arguments.get("remote_friendly"),
            limit=arguments.get("limit", 10),
        )
        return {
            "count": len(jobs),
            "jobs": [job.to_dict() for job in jobs],
        }

    async def _search_jobs(self, arguments: Dict) -> Dict:
        """Execute search_jobs tool."""
        keyword = arguments.get("keyword", "")
        limit = arguments.get("limit", 5)

        jobs = search_jobs(self.db, keyword, limit=limit)

        return {
            "search_term": keyword,
            "total_results": len(jobs),
            "jobs": [job.to_dict() for job in jobs],
        }

    async def _get_job_details(self, arguments: Dict) -> Dict:
        """Execute get_job_details tool."""
        job_id = arguments.get("job_id")
        if not job_id:
            return {"error": "Job ID is required"}

        job = get_job_by_id(self.db, job_id)
        if not job:
            return {"error": f"Job with ID '{job_id}' not found"}

        job_details = job.to_dict()
        job_details["applications_count"] = len(job.applications)

        return {
            "found": True,
            "job": job_details,
        }

    async def _get_job_categories(self, arguments: Dict) -> Dict:
        """Execute get_job_categories tool."""
        categories = get_job_categories(self.db)
        return {
            "categories": categories,
        }

    async def _get_job_stats(self, arguments: Dict) -> Dict:
        """Execute get_job_stats tool."""
        stats = get_job_stats(self.db)
        return {
            "stats": stats,
        }

    async def _create_job_listing(self, arguments: Dict) -> Dict:
        """Execute create_job_listing tool."""
        job_data = {
            "title": arguments.get("title"),
            "company": arguments.get("company"),
            "location": arguments.get("location"),
            "job_type": arguments.get("job_type"),
            "industry": arguments.get("industry"),
            "experience_level": arguments.get("experience_level"),
            "description": arguments.get("description"),
            "salary_range": arguments.get("salary_range", ""),
            "requirements": arguments.get("requirements", []),
            "benefits": arguments.get("benefits", []),
            "remote_friendly": arguments.get("remote_friendly", False),
        }

        job = create_job(self.db, job_data)

        return {
            "success": True,
            "message": "Job created successfully",
            "job_id": job.id,
            "job": job.to_dict(),
        }


async def execute_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Execute an MCP tool - standalone function for the AI assistant."""
    executor = MCPToolExecutor()
    try:
        result = await executor.execute(tool_name, arguments)
        return result
    finally:
        executor.close()
