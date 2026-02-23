"""FastAPI Streaming Router for MediRoute AI."""
import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from models.mediroute_models import MediRouteRequest
from services.mediroute_streaming_service import mediroute_streaming_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["MediRoute AI Streaming"])


@router.post("/analyze-stream")
async def analyze_stream(request: MediRouteRequest):
    """Submit patient intake info to MediRoute AI for routing with streaming updates."""

    if not request.symptoms.strip():
        raise HTTPException(status_code=400, detail="symptoms cannot be empty.")
    if not request.location.strip():
        raise HTTPException(status_code=400, detail="location cannot be empty.")
    if not request.insurance.strip():
        raise HTTPException(status_code=400, detail="insurance cannot be empty.")

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate Server-Sent Events for streaming updates."""
        try:
            async for event in mediroute_streaming_service.process_stream(
                session_id=request.session_id,
                symptoms=request.symptoms,
                location=request.location,
                insurance=request.insurance,
                current_situation=request.current_situation,
            ):
                # Format as SSE (Server-Sent Events)
                yield f"data: {json.dumps(event)}\n\n"

        except Exception as e:
            logger.error("Error during streaming: %s", e, exc_info=True)
            error_event = {
                "type": "error",
                "data": {
                    "message": str(e),
                    "session_id": request.session_id,
                }
            }
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable buffering in nginx
        },
    )
