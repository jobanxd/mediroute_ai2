"""MediRoute Service."""
import logging

from typing import Dict, Optional
from langchain_core.messages import HumanMessage, AIMessage

from agents.graph import graph

logger = logging.getLogger(__name__)


class MediRouteService:
    """Service to handle single-invocation MediRoute AI flows."""

    async def process(
        self,
        session_id: str,
        symptoms: str,
        location: str,
        insurance: str,
        current_situation: Optional[str] = None,
    ) -> Dict:
        """Invoke the agent graph with patient intake data."""

        final_state = await graph.ainvoke(
            {
                "symptoms": symptoms,
                "location": location,
                "insurance": insurance,
                "current_situation": current_situation,
            }
        )

        report_output = final_state.get("report_output")

        if not report_output or not report_output.get("generated"):
            logger.warning("Report was not generated.")
            return {
                "session_id": session_id,
                "success": False,
                "reason": report_output.get("reason", "Something went wrong. Please try again.") if report_output else "No report output found.",
            }

        return {
            "session_id": session_id,
            "success": True,
            "report": report_output,
        }

# Singleton
mediroute_service = MediRouteService()
