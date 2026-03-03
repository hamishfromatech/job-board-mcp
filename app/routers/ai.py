"""AI Assistant routes."""

from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_template_context
from app.services.ai_assistant import AIAssistant, OLLAMA_HOST, DEFAULT_MODEL
from app.services.mcp_executor import execute_mcp_tool

router = APIRouter(tags=["ai"])

# Initialize AI Assistant
ai_assistant = AIAssistant()


# =============================================================================
# AI Assistant Pages
# =============================================================================

@router.get("/ai-assistant", response_class=HTMLResponse)
async def ai_assistant_page(request: Request, db: Session = Depends(get_db)):
    """AI Assistant page."""
    templates = Jinja2Templates(directory="templates")
    health = await ai_assistant.health_check()

    context = get_template_context(
        request, db,
        ai_status=health,
        ollama_host=OLLAMA_HOST,
        default_model=DEFAULT_MODEL,
    )
    return templates.TemplateResponse("ai_assistant.html", context)


# =============================================================================
# AI Assistant API
# =============================================================================

@router.post("/api/ai/chat")
async def chat_endpoint(
    message: str = Form(...),
    session_id: Optional[str] = Form("default"),
):
    """API endpoint for AI chat."""
    try:
        response = await ai_assistant.process_message(
            message=message,
            session_id=session_id,
            tool_executor=execute_mcp_tool,
        )
        return response
    except Exception as e:
        return {"type": "error", "content": f"Error: {str(e)}"}


@router.post("/api/ai/clear")
async def clear_endpoint(session_id: Optional[str] = Form("default")):
    """Clear AI conversation history."""
    ai_assistant.clear_conversation(session_id)
    return {"status": "cleared"}


@router.get("/api/ai/health")
async def health_endpoint():
    """Check AI assistant health status."""
    health = await ai_assistant.health_check()
    return health