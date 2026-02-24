"""FastAPI Router for MediRoute AI."""
import logging

from fastapi import APIRouter, HTTPException

from models.mediroute_chat_models import ChatRequest, ChatResponse
from services.mediroute_chat_service import chat_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["MediRoute AI"])

# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a message to MediRoute AI and get a response."""

    if not request.user_input.strip():
        raise HTTPException(status_code=400, detail="user_input cannot be empty.")

    try:
        result = await chat_service.process_message(
            session_id=request.session_id,
            user_input=request.user_input,
        )

        return ChatResponse(
            session_id=result["session_id"],
            response=result["response"],
            agent_name=result.get("agent_name"),
            next_agent=result.get("next_agent")
        )

    except Exception as e:
        logger.error("Error processing message: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e
