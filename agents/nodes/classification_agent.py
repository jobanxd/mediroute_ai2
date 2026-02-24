"""Intake agent node for extracting patient information."""
import logging
import json

from langchain_core.messages import AIMessage

from agents.state import AgentState
from agents.prompts import classification_agent_prompts as ca_prompts
from utils.llm_util import call_llm

logger = logging.getLogger(__name__)


async def classification_agent_node(state: AgentState) -> AgentState:
    """
    Intake agent node — single pass extraction of patient info into structured JSON.
    """
    logger.info("="*30)
    logger.info("Classification Agent Node")
    logger.info("="*30)

    state_messages = state["messages"]

    # Build messages for LLM call
    messages = [
        {"role": "system", "content": ca_prompts.CLASSIFICATION_AGENT_SYSTEM_PROMPT}
    ]

    for msg in state_messages:
        role = "assistant" if isinstance(msg, AIMessage) else "user"
        content = msg.content
        messages.append({"role": role, "content": content})

    logger.info("Calling LLM with messages: %s", json.dumps(messages, indent=2))

    response = await call_llm(
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "intake_response",
                "schema": {
                    "type": "object",
                    "properties": {
                        "symptoms": {
                            "type": "string",
                            "description": "Patient symptoms in plain clinical language"
                        },
                        "classification_type": {
                            "type": "string",
                            "description": "One of the 6 predefined classification types"
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["CRITICAL", "URGENT", "MODERATE"]
                        },
                        "confidence": {
                            "type": "string",
                            "enum": ["HIGH", "MEDIUM", "LOW"]
                        },
                        "classification_rationale": {
                            "type": "string",
                            "description": "One sentence explaining the classification decision"
                        },
                        "dispatch_required": {
                            "type": "boolean"
                        },
                        "dispatch_rationale": {
                            "type": "string",
                            "description": "One sentence explaining the dispatch decision"
                        },
                        "location": {
                            "type": "string",
                            "description": "Extracted location"
                        },
                        "insurance_provider": {
                            "type": "string",
                            "description": "Normalized insurance provider name"
                        },
                        "preferred_hospital": {
                            "type": "string",
                            "description": "Preferred hospital of the patient"
                        }
                    },
                    "required": [
                        "symptoms",
                        "classification_type",
                        "severity",
                        "confidence",
                        "classification_rationale",
                        "dispatch_required",
                        "dispatch_rationale",
                        "location",
                        "insurance_provider",
                        "preferred_hospital"
                    ],
                }
            }
        }
    )

    logger.info("LLM response: \n%s", response)

    # Parse JSON response
    message = response.choices[0].message
    raw_content = message.content or ""

    try:
        extracted = json.loads(raw_content)
        logger.info("Extracted intake data: %s", json.dumps(extracted, indent=2))
    except json.JSONDecodeError as e:
        logger.error("Failed to parse intake JSON: %s | Raw: %s", e, raw_content)
        extracted = {
            "symptoms": "unknown",
            "classification_type": "GENERAL",
            "location": "unknown",
            "insurance_provider": "unknown"
        }

    summary = extracted.pop("summary", "Classification complete. Routing to hospital matching.")

    # Store as stringified JSON in the message so match_agent can parse it
    return {
        "messages": [AIMessage(content=summary, name="classification_agent")],
        "classification_agent_output": extracted,
        "next_agent": "match_agent"
    }
