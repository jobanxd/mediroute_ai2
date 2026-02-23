"""FastAPI Router for MediRoute AI."""
import logging

from fastapi import APIRouter, HTTPException

from models.mediroute_models import MediRouteRequest, MediRouteResponse
from services.mediroute_service import mediroute_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["MediRoute AI"])

@router.post("/analyze", response_model=MediRouteResponse)
async def analyze(request: MediRouteRequest):
    """Submit patient intake info to MediRoute AI for routing."""

    if not request.symptoms.strip():
        raise HTTPException(status_code=400, detail="symptoms cannot be empty.")
    if not request.location.strip():
        raise HTTPException(status_code=400, detail="location cannot be empty.")
    if not request.insurance.strip():
        raise HTTPException(status_code=400, detail="insurance cannot be empty.")

    try:
        result = await mediroute_service.process(
            session_id=request.session_id,
            symptoms=request.symptoms,
            location=request.location,
            insurance=request.insurance,
            current_situation=request.current_situation,
        )

        return MediRouteResponse(**result)

    except Exception as e:
        logger.error("Error processing request: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e
