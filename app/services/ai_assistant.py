"""Ollama AI Assistant service for job board."""

import json
import os
from typing import Any, Callable, Dict, List, Optional

import httpx

from app.config import settings


OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "glm-5:cloud")


class OllamaClient:
    """Client for Ollama API."""

    def __init__(self, host: str = OLLAMA_HOST, model: str = DEFAULT_MODEL):
        self.host = host.rstrip("/")
        self.model = model
        self.client = httpx.AsyncClient(timeout=120.0)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Send a chat request to Ollama."""
        url = f"{self.host}/api/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": 0.7,
            },
        }

        if tools:
            payload["tools"] = tools

        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            return {
                "error": f"Could not connect to Ollama at {self.host}. Make sure Ollama is running.",
                "message": {"content": "I'm sorry, I can't connect to Ollama. Please make sure it's running."},
            }
        except Exception as e:
            return {
                "error": str(e),
                "message": {"content": f"Error: {str(e)}"},
            }

    async def list_models(self) -> List[str]:
        """List available models from Ollama."""
        try:
            response = await self.client.get(f"{self.host}/api/tags")
            data = response.json()
            return [m["name"] for m in data.get("models", [])]
        except:
            return []

    def close(self):
        """Close the HTTP client."""
        self.client.aclose()


# Define MCP tools for the AI
MCP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_jobs",
            "description": "Get available jobs with optional filtering by location, industry, job type, and remote preference",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Filter by location (e.g., 'Mackay')",
                    },
                    "industry": {
                        "type": "string",
                        "description": "Filter by industry (e.g., 'Technology', 'Mining', 'Healthcare')",
                    },
                    "job_type": {
                        "type": "string",
                        "description": "Filter by job type (Full-time, Part-time, Contract, Casual)",
                    },
                    "remote_friendly": {
                        "type": "boolean",
                        "description": "Filter for remote-friendly positions",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of jobs to return",
                        "default": 10,
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_jobs",
            "description": "Search for jobs by keyword in title, company, description, or requirements",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Search keyword (e.g., 'Python', 'manager', 'remote')",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 5,
                    },
                },
                "required": ["keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_job_details",
            "description": "Get detailed information about a specific job by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "The unique job ID (UUID)",
                    },
                },
                "required": ["job_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_job_categories",
            "description": "Get available job categories, industries, and experience levels",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_job_stats",
            "description": "Get statistics about the job board (total jobs, by industry, etc.)",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_job_listing",
            "description": "Create a new job listing on the job board",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Job title",
                    },
                    "company": {
                        "type": "string",
                        "description": "Company name",
                    },
                    "location": {
                        "type": "string",
                        "description": "Job location",
                    },
                    "job_type": {
                        "type": "string",
                        "description": "Job type (Full-time, Part-time, Contract, Casual)",
                    },
                    "industry": {
                        "type": "string",
                        "description": "Industry category",
                    },
                    "experience_level": {
                        "type": "string",
                        "description": "Experience level (Entry, Mid, Senior, Executive)",
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed job description",
                    },
                    "salary_range": {
                        "type": "string",
                        "description": "Salary range text (optional)",
                    },
                    "requirements": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of job requirements",
                    },
                    "benefits": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of job benefits",
                    },
                    "remote_friendly": {
                        "type": "boolean",
                        "description": "Whether the job is remote-friendly",
                    },
                },
                "required": ["title", "company", "location", "job_type", "industry", "experience_level", "description"],
            },
        },
    },
]


SYSTEM_PROMPT = """You are an AI assistant for a Job Board system. You help users find jobs, view job details, and create job listings.

You have access to tools that let you interact with the job board database. When a user asks about jobs, use the appropriate tool to fetch information.

Guidelines:
- Be friendly and professional
- When searching jobs, summarize the results in a helpful way
- If creating a job, confirm the details before calling the tool
- If you don't have enough information, ask the user for clarification
- Always explain what actions you're taking

The job board focuses on jobs in Mackay, Queensland, Australia, but supports various locations."""


class AIAssistant:
    """AI Assistant that uses Ollama and MCP tools."""

    def __init__(self, ollama_host: str = OLLAMA_HOST, model: str = DEFAULT_MODEL):
        self.ollama = OllamaClient(ollama_host, model)
        self.conversations: Dict[str, List[Dict]] = {}

    def get_conversation(self, session_id: str) -> List[Dict]:
        """Get or create a conversation history."""
        if session_id not in self.conversations:
            self.conversations[session_id] = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
        return self.conversations[session_id]

    def clear_conversation(self, session_id: str):
        """Clear a conversation history."""
        if session_id in self.conversations:
            del self.conversations[session_id]

    async def process_message(
        self,
        message: str,
        session_id: str,
        tool_executor: Callable[[str, Dict], Any],
    ) -> Dict[str, Any]:
        """Process a user message and return a response."""
        conversation = self.get_conversation(session_id)
        conversation.append({"role": "user", "content": message})

        # First call - see if AI wants to use tools
        response = await self.ollama.chat(conversation, tools=MCP_TOOLS)

        if "error" in response:
            return {
                "type": "error",
                "message": response["error"],
                "content": response["message"]["content"],
            }

        assistant_message = response.get("message", {})
        tool_calls = assistant_message.get("tool_calls", [])

        # Execute any tool calls
        tool_results = []
        if tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call.get("function", {}).get("name")
                arguments = tool_call.get("function", {}).get("arguments", {})

                if isinstance(arguments, str):
                    arguments = json.loads(arguments)

                try:
                    result = await tool_executor(function_name, arguments)
                    tool_results.append({
                        "tool": function_name,
                        "arguments": arguments,
                        "result": result,
                    })
                except Exception as e:
                    tool_results.append({
                        "tool": function_name,
                        "arguments": arguments,
                        "error": str(e),
                    })

            # Add tool results to conversation
            tool_message = "Tool results:\n"
            for result in tool_results:
                if "error" in result:
                    tool_message += f"- {result['tool']}: Error - {result['error']}\n"
                else:
                    tool_message += f"- {result['tool']}: Success\n"

            conversation.append({
                "role": "tool",
                "content": tool_message,
            })

            # Second call - get final response with tool results
            response = await self.ollama.chat(conversation)
            assistant_message = response.get("message", {})

        content = assistant_message.get("content", "I'm sorry, I couldn't process that.")
        conversation.append({"role": "assistant", "content": content})

        return {
            "type": "success",
            "content": content,
            "tool_calls": tool_results if tool_calls else None,
        }

    async def chat_without_tools(self, message: str, session_id: str) -> str:
        """Simple chat without tool calling."""
        conversation = self.get_conversation(session_id)
        conversation.append({"role": "user", "content": message})

        response = await self.ollama.chat(conversation)
        content = response.get("message", {}).get("content", "I'm sorry, I couldn't respond.")

        conversation.append({"role": "assistant", "content": content})
        return content

    async def health_check(self) -> Dict[str, Any]:
        """Check if Ollama is available."""
        models = await self.ollama.list_models()
        return {
            "status": "ok" if models else "error",
            "models": models,
            "using_model": self.ollama.model,
        }
