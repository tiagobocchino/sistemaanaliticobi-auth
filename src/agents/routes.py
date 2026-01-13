"""
Agent routes for chat and status.
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.auth.dependencies import get_current_user
from src.agents.agno_agent import analytics_agent

router = APIRouter(prefix="/agents", tags=["Agents"])


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat(request: ChatRequest, current_user=Depends(get_current_user)) -> Dict[str, Any]:
    """Send a message to the analytics agent."""
    try:
        permissions = await analytics_agent.check_user_permissions(current_user.id)
        result = await analytics_agent.process_query(
            user_id=current_user.id,
            query=request.message,
            permissions=permissions,
        )
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent error: {exc}",
        )


@router.get("/capabilities")
async def capabilities() -> Dict[str, Any]:
    """List agent capabilities."""
    tools = []
    if getattr(analytics_agent, "agent", None):
        tools = [tool.__name__ for tool in analytics_agent.agent.tools]
    return {"tools": tools}


@router.get("/health")
async def health() -> Dict[str, Any]:
    """Health endpoint for the agent."""
    return {"status": "ok"}
