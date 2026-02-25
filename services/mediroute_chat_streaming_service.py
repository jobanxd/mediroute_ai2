"""Chat Service for MediRoute AI — with streaming support."""
import json
import logging
from typing import AsyncGenerator, Dict, List

from langchain_core.messages import AIMessage, HumanMessage

from agents.graph import graph
from agents.state import AgentState

logger = logging.getLogger(__name__)

# ── Node display names & status messages ──────────────────────────────────────
NODE_STATUS_MESSAGES: Dict[str, str] = {
     "verification_agent":   "🔐 Verifying insurance eligibility...", 
    "orchestrator_agent":   "🧠 Orchestrator is analyzing your request...",
    "classification_agent": "🏥 Classifying emergency details...",
    "match_agent":          "🔍 Matching available hospitals and services...",
    "loa_agent":            "📋 Generating Letter of Authorization...",
    "report_agent":         "📝 Compiling medical report...",
    "response_agent":       "💬 Preparing your response...",
}

# The top-level graph name emitted by LangGraph in astream_events
# This is the event name for the full graph run finishing
_GRAPH_ROOT_NAME = "LangGraph"


class ChatService:
    """Service to handle chat interactions and maintain session state."""

    def __init__(self):
        self.sessions: Dict[str, AgentState] = {}

    def _get_or_create_session(self, session_id: str, patient_name: str = "") -> AgentState:
        if session_id not in self.sessions:
            self.sessions[session_id] = AgentState(
                messages=[],
                patient_name=patient_name,
                next_agent="",
                classification_agent_output=None,
                selected_loa_services=[],
                match_agent_output=None,
                chosen_hospital=None,
                loa_output=None,
                report_output=None,
            )
            logger.info("NEW SESSION | Session: %s | Patient: %s", session_id, patient_name)
        else:
            logger.info("EXISTING SESSION | Session: %s", session_id)
        return self.sessions[session_id]

    # ── Non-streaming (kept for backwards compat) ─────────────────────────────
    async def process_message(self, session_id: str, patient_name: str, user_input: str) -> Dict:
        """Process a message and return the full final response (no streaming)."""
        current_state = self._get_or_create_session(session_id, patient_name)
        current_state["messages"].append(HumanMessage(content=user_input))
        logger.info("USER: %s", user_input)

        final_state = await graph.ainvoke(current_state)
        self.sessions[session_id] = final_state

        return self._build_result(session_id, final_state)


    # ── Streaming ─────────────────────────────────────────────────────────────
    async def stream_message(
        self, session_id: str, patient_name: str, user_input: str
    ) -> AsyncGenerator[str, None]:
        """
        Yields SSE-formatted strings as the graph executes.

        Event types emitted:
          • "node_start"   — a node just began executing
          • "node_done"    — a node finished (with optional extracted data)
          • "final"        — graph is done; carries the full result payload
          • "error"        — something went wrong
        """
        current_state = self._get_or_create_session(session_id, patient_name)

        # Append user message ONCE before invoking — this becomes part of history
        current_state["messages"].append(HumanMessage(content=user_input))
        logger.info("USER (stream): %s", user_input)
        logger.info(
            "Messages in session before invoke: %d",
            len(current_state["messages"])
        )

        # We'll capture the authoritative final state from the graph's own
        # on_chain_end event, which contains the complete merged state
        # including the full updated messages list.
        final_state: AgentState | None = None

        try:
            async for event in graph.astream_events(current_state, version="v2"):
                event_name = event.get("event")
                node_name  = event.get("name", "")

                # ── Node started ──────────────────────────────────────────────
                if event_name == "on_chain_start" and node_name in NODE_STATUS_MESSAGES:
                    logger.debug("Node started: %s", node_name)
                    yield self._sse(
                        "node_start",
                        {
                            "node":    node_name,
                            "message": NODE_STATUS_MESSAGES[node_name],
                        },
                    )

                # ── Node finished ─────────────────────────────────────────────
                elif event_name == "on_chain_end" and node_name in NODE_STATUS_MESSAGES:
                    output = event.get("data", {}).get("output", {}) or {}
                    logger.debug("Node done: %s | output keys: %s", node_name, list(output.keys()))

                    yield self._sse(
                        "node_done",
                        {
                            "node":    node_name,
                            "message": self._done_message(node_name),
                            "data":    self._node_public_data(node_name, output),
                        },
                    )

                # ── TOP-LEVEL GRAPH finished — capture authoritative state ────
                #
                # LangGraph emits an on_chain_end for the root graph itself.
                # Its output IS the complete final state with all messages merged.
                # This is the ONLY reliable place to get the full updated state.
                elif event_name == "on_chain_end" and node_name == _GRAPH_ROOT_NAME:
                    output = event.get("data", {}).get("output", {}) or {}
                    if output:
                        final_state = output
                        logger.info(
                            "Graph completed. Final message count: %d",
                            len(final_state.get("messages", []))
                        )

            # ── Persist the authoritative final state ─────────────────────────
            if final_state:
                self.sessions[session_id] = final_state
            else:
                # Fallback: if we somehow missed the graph end event,
                # keep current_state as-is (history is at least preserved
                # because we appended the user message before invoking)
                logger.warning(
                    "Graph end event not captured for session %s. "
                    "State may be incomplete.",
                    session_id
                )
                self.sessions[session_id] = current_state

            result = self._build_result(session_id, self.sessions[session_id])
            yield self._sse("final", result)

        except Exception as exc:
            logger.error("Stream error for session %s: %s", session_id, exc, exc_info=True)
            # Still persist whatever state we have so history isn't wiped
            self.sessions[session_id] = current_state
            yield self._sse("error", {"detail": str(exc)})

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _sse(event_type: str, payload: dict) -> str:
        """Format a Server-Sent Event string."""
        data = json.dumps({"type": event_type, **payload}, default=str)
        return f"data: {data}\n\n"

    @staticmethod
    def _done_message(node_name: str) -> str:
        messages = {
            "verification_agent":   "✅ Insurance verified.",
            "orchestrator_agent":   "✅ Request analyzed.",
            "classification_agent": "✅ Emergency classified.",
            "match_agent":          "✅ Hospitals matched.",
            "loa_agent":            "✅ LOA generated.",
            "report_agent":         "✅ Report compiled.",
            "response_agent":       "✅ Response ready.",
        }
        return messages.get(node_name, "✅ Done.")

    @staticmethod
    def _node_public_data(node_name: str, output: dict) -> dict:
        """
        Control exactly what intermediate data reaches the FE per node.
        Reads directly from the node's own output dict (not full session state)
        so there is no risk of stale/wrong values.
        """
        if node_name == "verification_agent":
            return {"verfication": output.get("verification_output")}
        if node_name == "classification_agent":
            return {"classification": output.get("classification_agent_output")}
        if node_name == "match_agent":
            return {"matched_hospitals": output.get("match_agent_output")}
        if node_name == "loa_agent":
            return {"loa_output": output.get("loa_output")}
        if node_name == "report_agent":
            return {"report_output": output.get("report_output")}
        return {}

    def _build_result(self, session_id: str, state: AgentState) -> dict:
        """Build the final response dict from the completed state."""
        messages = state.get("messages", [])
        logger.info(
            "Building result for session %s | total messages: %d",
            session_id, len(messages)
        )

        ai_message = next(
            (m for m in reversed(messages) if isinstance(m, AIMessage)), None
        )

        if not ai_message:
            logger.warning("No AI message found in final state for session %s.", session_id)
            return {
                "session_id":    session_id,
                "response":      "Something went wrong. Please try again.",
                "next_agent":    state.get("next_agent", "unknown"),
                "agent_name":    None,
                "loa_output":    state.get("loa_output", {}),
                "report_output": state.get("report_output", {}),
            }

        return {
            "session_id":    session_id,
            "response":      ai_message.content,
            "next_agent":    state.get("next_agent", "unknown"),
            "agent_name":    getattr(ai_message, "name", None),
            "loa_output":    state.get("loa_output", {}),
            "report_output": state.get("report_output", {}),
        }

    def get_session_history(self, session_id: str) -> List:
        return self.sessions.get(session_id, {}).get("messages", [])


# Singleton
chat_service = ChatService()