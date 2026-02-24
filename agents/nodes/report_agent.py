import logging
import json

from agents.state import AgentState
from agents.prompts import report_agent_prompts as ra_prompts
from utils.llm_util import call_llm

logger = logging.getLogger(__name__)


async def report_agent_node(state: AgentState) -> AgentState:
    """
    Report agent node — generates a full patient admission summary
    and confirms hospital admission details.
    """
    logger.info("=" * 30)
    logger.info("Report Agent Node")
    logger.info("=" * 30)

    ca_output = state["classification_agent_output"]
    dispatch_required = ca_output.get("dispatch_required", True)
    dispatch_rationale = ca_output.get("dispatch_rationale", "")
    loa_output = state["loa_output"]

    # ── LLM Call: case_summary, recommendation_reason, next_steps ────────────
    messages = [
        {"role": "system", "content": ra_prompts.REPORT_AGENT_SYSTEM_PROMPT},
        {"role": "user", "content": ra_prompts.REPORT_AGENT_QUERY_PROMPT.format(
            symptoms=loa_output["symptoms"],
            current_situation=loa_output["current_situation"],
            classification_type=loa_output["classification_type"],
            severity=loa_output["severity"],
            insurance_provider=loa_output["insurance_provider"],
            hospital_name=loa_output["hospital_name"],
            hospital_address=loa_output["address"],
            contact=loa_output["contact"],
            emergency_contact=loa_output["emergency_contact"],
            distance_km=loa_output["distance_km"],
            loa_number=loa_output["loa_number"],
            valid_until=loa_output["valid_until"],
            approved_services=json.dumps(loa_output["approved_services"], indent=2),
            room_type=loa_output["room_type"],
            exclusions=json.dumps(loa_output["exclusions"], indent=2),
            clinical_justification=loa_output["clinical_justification"],
            remarks=loa_output["remarks"],
        )}
    ]

    logger.info("Calling LLM for report generation...")

    response = await call_llm(
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "report_fields",
                "schema": {
                    "type": "object",
                    "properties": {
                        "case_summary": {"type": "string"},
                        "hospital_recommendation_reason": {"type": "string"},
                        "next_steps": {"type": "string"},
                    },
                    "required": [
                        "case_summary",
                        "hospital_recommendation_reason",
                        "next_steps"
                    ],
                },
            },
        }
    )

    raw_content = response.choices[0].message.content or ""

    try:
        llm_fields = json.loads(raw_content)
        case_summary = llm_fields.get("case_summary", "")
        hospital_recommendation_reason = llm_fields.get("hospital_recommendation_reason", "")
        next_steps = llm_fields.get("next_steps", "")
    except json.JSONDecodeError as e:
        logger.error("Failed to parse report fields: %s | Raw: %s", e, raw_content)
        case_summary = f"Emergency case: {loa_output['classification_type']} — {loa_output['symptoms']}"
        hospital_recommendation_reason = f"{loa_output['hospital_name']} was selected based on proximity, insurance accreditation, and required medical capabilities."
        next_steps = f"Proceed immediately to {loa_output['hospital_name']}. Present your LOA number {loa_output['loa_number']} at the emergency desk."

    # ── Assemble full report ──────────────────────────────────────────────────
    report_output = {
        "generated": True,
        # Case overview (LLM)
        "case_summary": case_summary,
        "hospital_recommendation_reason": hospital_recommendation_reason,
        "next_steps": next_steps,
        # Patient situation
        "symptoms": loa_output["symptoms"],
        "current_situation": loa_output["current_situation"],
        "classification_type": loa_output["classification_type"],
        "severity": loa_output["severity"],
        "dispatch_required": dispatch_required,
        "dispath_rationale": dispatch_rationale,
        # Insurance
        "insurance_provider": loa_output["insurance_provider"],
        # LOA details
        "loa_number": loa_output["loa_number"],
        "date_issued": loa_output["date_issued"],
        "valid_until": loa_output["valid_until"],
        "clinical_justification": loa_output["clinical_justification"],
        "remarks": loa_output["remarks"],
        # Hospital
        "hospital_id": loa_output["hospital_id"],
        "hospital_name": loa_output["hospital_name"],
        "address": loa_output["address"],
        "contact": loa_output["contact"],
        "emergency_contact": loa_output["emergency_contact"],
        "distance_km": loa_output["distance_km"],
        # Coverage
        "approved_services": loa_output["approved_services"],
        "room_type": loa_output["room_type"],
        "exclusions": loa_output["exclusions"],
    }

    logger.info("Report generated for LOA: %s", loa_output["loa_number"])
    logger.info("Report Agent output: %s", json.dumps(
        {k: v for k, v in report_output.items()}, indent=2
    ))

    return {
        "report_output": report_output,
        "next_agent": "end"
    }