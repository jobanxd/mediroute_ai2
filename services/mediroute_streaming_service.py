"""MediRoute Streaming Service."""
import logging
from typing import AsyncGenerator, Dict, Optional

from agents.graph import graph

logger = logging.getLogger(__name__)

# Node name mapping for user-friendly messages
NODE_DISPLAY_NAMES = {
    "classification_agent": "Classification Agent",
    "match_agent": "Hospital Matching Agent",
    "loa_agent": "Letter of Authorization Agent",
    "report_agent": "Report Generation Agent",
}

NODE_DESCRIPTIONS = {
    "classification_agent": "Analyzing symptoms and classifying urgency...",
    "match_agent": "Finding suitable hospitals based on your needs...",
    "loa_agent": "Generating Letter of Authorization...",
    "report_agent": "Preparing comprehensive medical report...",
}


class MediRouteStreamingService:
    """Service to handle streaming MediRoute AI flows."""

    async def process_stream(
        self,
        session_id: str,
        symptoms: str,
        location: str,
        insurance: str,
        current_situation: Optional[str] = None,
    ) -> AsyncGenerator[Dict, None]:
        """
        Invoke the agent graph with patient intake data and stream updates.
        
        Yields events in the format:
        {
            "type": "node_start" | "node_complete" | "final_result" | "error",
            "data": {...}
        }
        """
        
        input_data = {
            "symptoms": symptoms,
            "location": location,
            "insurance": insurance,
            "current_situation": current_situation,
        }

        try:
            # Send initial event
            yield {
                "type": "start",
                "data": {
                    "session_id": session_id,
                    "message": "Processing started...",
                }
            }

            # Track nodes for progress
            node_order = [
                "classification_agent",
                "match_agent",
                "loa_agent",
                "report_agent"
            ]
            current_node_index = 0
            total_nodes = len(node_order)
            final_state = None

            # Use astream to get updates as each node completes
            async for chunk in graph.astream(input_data):
                logger.info(f"Received chunk: {chunk.keys()}")
                
                # chunk is a dict with node name as key
                for node_name, node_output in chunk.items():
                    if node_name in node_order:
                        current_node_index = node_order.index(node_name) + 1
                        
                        # Store the latest state
                        final_state = node_output
                        
                        # Send node completion event
                        yield {
                            "type": "node_complete",
                            "data": {
                                "session_id": session_id,
                                "node": node_name,
                                "node_display_name": NODE_DISPLAY_NAMES.get(node_name, node_name),
                                "progress": {
                                    "current": current_node_index,
                                    "total": total_nodes,
                                    "percentage": int((current_node_index / total_nodes) * 100)
                                },
                                "message": f"Completed: {NODE_DISPLAY_NAMES.get(node_name, node_name)}",
                            }
                        }
                        
                        # If there's a next node, send node_start event
                        if current_node_index < total_nodes:
                            next_node = node_order[current_node_index]
                            yield {
                                "type": "node_start",
                                "data": {
                                    "session_id": session_id,
                                    "node": next_node,
                                    "node_display_name": NODE_DISPLAY_NAMES.get(next_node, next_node),
                                    "message": NODE_DESCRIPTIONS.get(next_node, f"Starting {next_node}..."),
                                    "progress": {
                                        "current": current_node_index,
                                        "total": total_nodes,
                                        "percentage": int((current_node_index / total_nodes) * 100)
                                    }
                                }
                            }

            # Use the final state from the stream (no need to invoke again!)
            report_output = final_state.get("report_output") if final_state else None

            if not report_output or not report_output.get("generated"):
                logger.warning("Report was not generated.")
                yield {
                    "type": "final_result",
                    "data": {
                        "session_id": session_id,
                        "success": False,
                        "reason": report_output.get("reason", "Something went wrong. Please try again.") if report_output else "No report output found.",
                    }
                }
            else:
                yield {
                    "type": "final_result",
                    "data": {
                        "session_id": session_id,
                        "success": True,
                        "report": report_output,
                    }
                }

        except Exception as e:
            logger.error(f"Error in streaming process: {e}", exc_info=True)
            yield {
                "type": "error",
                "data": {
                    "session_id": session_id,
                    "message": str(e),
                }
            }


# Singleton
mediroute_streaming_service = MediRouteStreamingService()
