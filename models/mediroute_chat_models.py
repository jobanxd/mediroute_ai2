"""Models for chat request and response."""
from typing import Optional
from pydantic import BaseModel

from agents.state import LOAOutput, ReportOutput


class ChatRequest(BaseModel):
    """Request model for chat interactions."""
    session_id: str
    patient_name: str
    user_input: str


class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    session_id: str
    response: str
    agent_name: Optional[str] = None