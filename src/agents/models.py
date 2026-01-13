"""
Pydantic models for agent requests/responses.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str = "user"
    content: str


class AgentQuery(BaseModel):
    intent: str
    data_sources: List[str]
    entities: Dict[str, Any]


class APIResponse(BaseModel):
    source: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AgentResponse(BaseModel):
    message: str
    confidence: Optional[float] = None
    data_source: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    charts: Optional[List[Dict[str, Any]]] = None
    explanation: Optional[str] = None
    rag_sources: Optional[List[Dict[str, Any]]] = None


class Conversation(BaseModel):
    user_id: str
    messages: List[ChatMessage]
