"""Intake agent node for extracting patient information."""
import logging
import json

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

    symptoms = state["symptoms"]
    location = state["location"]
    insurance = state["insurance"]
    current_situation = state["current_situation"]

    # Build messages for LLM call
    messages = [
        {"role": "system", "content": ca_prompts.CLASSIFICATION_AGENT_SYSTEM_PROMPT},
        {"role": "user", "content": ca_prompts.CLASSIFICATION_AGENT_QUERY_PROMPT.format(
            symptoms=symptoms,
            location=location,
            insurance=insurance,
            current_situation=current_situation,
        )}
    ]

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
                        "symptoms": {"type": "string"},
                        "classification_type": {"type": "string"},
                        "location": {"type": "string"},
                        "insurance_provider": {"type": "string"},
                    },
                    "required": [
                        "symptoms",
                        "classification_type",
                        "location",
                        "insurance_provider",
                    ],
                },
            },
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

    # Store as stringified JSON in the message so match_agent can parse it
    return {
        "classification_agent_output": extracted,
        "next_agent": "match_agent"
    }
