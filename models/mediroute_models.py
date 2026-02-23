"""Mediroute Models"""
from typing import Optional
from pydantic import BaseModel


class MediRouteRequest(BaseModel):
    """Request model for MediRoute AI."""
    session_id: str
    symptoms: str
    location: str
    insurance: str
    current_situation: Optional[str] = None


class MediRouteResponse(BaseModel):
    """Response model for MediRoute AI."""
    session_id: str
    success: bool
    report: Optional[dict] = None
    reason: Optional[str] = None
