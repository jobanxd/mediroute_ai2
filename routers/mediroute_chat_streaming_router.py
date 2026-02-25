"""FastAPI Router for MediRoute AI."""
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from models.mediroute_chat_models import ChatRequest, ChatResponse
from services.mediroute_chat_streaming_service import chat_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["MediRoute AI"])


# ── Regular (non-streaming) ───────────────────────────────────────────────────
@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a message and get a single complete response."""
    if not request.user_input.strip():
        raise HTTPException(status_code=400, detail="user_input cannot be empty.")

    try:
        result = await chat_service.process_message(
            session_id=request.session_id,
            patient_name=request.patient_name,
            user_input=request.user_input,
        )
        return ChatResponse(
            session_id=result["session_id"],
            response=result["response"],
            agent_name=result.get("agent_name"),
            next_agent=result.get("next_agent"),
            loa_output=result.get("loa_output"),
            report_output=result.get("report_output"),
        )
    except Exception as e:
        logger.error("Error processing message: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


# ── Streaming (SSE) ───────────────────────────────────────────────────────────
@router.post("/message/stream")
async def send_message_stream(request: ChatRequest):
    """
    Stream node-by-node progress via Server-Sent Events.

    Each SSE chunk is a JSON object with a `type` field:
      - node_start  → { type, node, message }
      - node_done   → { type, node, message, data }
      - final       → { type, session_id, response, agent_name, ... }
      - error       → { type, detail }
    """
    if not request.user_input.strip():
        raise HTTPException(status_code=400, detail="user_input cannot be empty.")

    return StreamingResponse(
        chat_service.stream_message(
            session_id=request.session_id,
            patient_name=request.patient_name,
            user_input=request.user_input,
        ),
        media_type="text/event-stream",
        headers={
            # Prevent buffering at the proxy/nginx layer
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )