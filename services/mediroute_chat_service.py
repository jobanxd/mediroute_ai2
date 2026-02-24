"""Chat Service for MediRoute AI."""
import logging

from typing import Dict, List
from langchain_core.messages import HumanMessage, AIMessage

from agents.graph import graph
from agents.state import AgentState

logger = logging.getLogger(__name__)


class ChatService:
    """Service to handle chat interactions and maintain session state."""
    def __init__(self):
        # Store full AgentState per session
        self.sessions: Dict[str, AgentState] = {}

    async def process_message(self, session_id: str, user_input: str) -> Dict:
        """Process user message and return response."""

        # Initialize session if not exist
        if session_id not in self.sessions:
            self.sessions[session_id] = AgentState(
                messages=[],
                next_agent="",
                classification_agent_output=None,
                selected_loa_services=[],
                match_agent_output=None,
                chosen_hospital=None,
                loa_output=None,
                report_output=None,
            )
            logger.info("NEW SESSION | Session: %s", session_id)
        else:
            logger.info("EXISTING SESSION | Session: %s", session_id)

        current_state = self.sessions[session_id]

        # Append user message to session history
        user_message = HumanMessage(content=user_input)
        current_state["messages"].append(user_message)

        logger.info("USER: %s", user_input)
        logger.info("Total messages in session: %s", len(current_state["messages"]))

        # --- Invoke Graph ---
        final_state = await graph.ainvoke(current_state)

        # Merge final state safely
        for key, value in final_state.items():
            if value is not None:
                current_state[key] = value

        # Save updated state back
        self.sessions[session_id] = current_state

        final_messages = current_state.get("messages", [])

        # Get last AI message
        ai_message = None
        for msg in reversed(final_messages):
            if isinstance(msg, AIMessage):
                ai_message = msg
                break

        if not ai_message:
            logger.warning("No AI message found in final state.")
            return {
                "session_id": session_id,
                "response": "Something went wrong. Please try again.",
                "next_agent": current_state.get("next_agent", "unknown"),
            }

        return {
            "session_id": session_id,
            "response": ai_message.content,
            "next_agent": current_state.get("next_agent", "unknown"),
            "agent_name": ai_message.name if hasattr(ai_message, "name") else None,
            "loa_output": current_state.get("loa_output", {}),
            "report_output": current_state.get("report_output", {})
        }

    def get_session_history(self, session_id: str) -> List:
        """Return message history for a given session ID."""
        return self.sessions.get(session_id, {}).get("messages", [])


# Singleton
chat_service = ChatService()