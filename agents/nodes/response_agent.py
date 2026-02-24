"""Response agent node — patient-facing messaging for Phase 1 and Phase 2."""
import logging

from langchain_core.messages import AIMessage

from agents.state import AgentState
from agents.prompts import response_agent_prompts as ra_prompts
from utils.llm_util import call_llm

logger = logging.getLogger(__name__)


# ── Phase 1 ───────────────────────────────────────────────────────────────────
async def _handle_phase1(state: AgentState) -> str:
    ca_output = state.get("classification_agent_output", {})
    match_output = state.get("match_agent_output", {})

    top_hospitals = match_output.get("top_hospitals", [])
    preferred_hospital_fail_reason = match_output.get("preferred_hospital_fail_reason")

    # Format hospital list for the prompt
    hospitals_text = "\n".join([
        f"{i+1}. {h['hospital_name']} — {h['distance_km']} km away\n"
        f"   Address: {h['address']}\n"
        f"   Emergency Contact: {h['emergency_contact']}"
        for i, h in enumerate(top_hospitals)
    ])

    messages = [
        {"role": "system", "content": ra_prompts.RESPONSE_AGENT_PHASE1_SYSTEM_PROMPT},
        {"role": "user", "content": ra_prompts.RESPONSE_AGENT_PHASE1_QUERY_PROMPT.format(
            symptoms=ca_output.get("symptoms", "unknown"),
            classification_type=ca_output.get("classification_type", "GENERAL"),
            severity=ca_output.get("severity", "URGENT"),
            recommended_action=ca_output.get("recommended_action", "HOSPITAL_ADMISSION"),
            dispatch_required=ca_output.get("dispatch_required", False),
            location=ca_output.get("location", "unknown"),
            insurance_provider=ca_output.get("insurance_provider", "unknown"),
            preferred_hospital=ca_output.get("preferred_hospital") or "None",
            preferred_hospital_fail_reason=preferred_hospital_fail_reason or "N/A",
            top_hospitals=hospitals_text,
        )}
    ]

    logger.info("Response agent Phase 1 — calling LLM...")

    response = await call_llm(messages=messages)
    return response.choices[0].message.content or "Please choose a hospital from the list above."


# ── Phase 2 ───────────────────────────────────────────────────────────────────
async def _handle_phase2(state: AgentState, report_output: dict) -> str:
    ca_output = state.get("classification_agent_output", {})
    assigned_doctor = report_output.get("assigned_doctor", {})

    messages = [
        {"role": "system", "content": ra_prompts.RESPONSE_AGENT_PHASE2_SYSTEM_PROMPT},
        {"role": "user", "content": ra_prompts.RESPONSE_AGENT_PHASE2_QUERY_PROMPT.format(
            symptoms=report_output.get("symptoms", ca_output.get("symptoms", "unknown")),
            classification_type=report_output.get("classification_type", "GENERAL"),
            severity=report_output.get("severity", "URGENT"),
            recommended_action=report_output.get("recommended_action", "HOSPITAL_ADMISSION"),
            dispatch_required=report_output.get("dispatch_required", False),
            dispatch_rationale=report_output.get("dispatch_rationale", "Not provided"),
            current_situation=report_output.get("current_situation", "Not provided"),
            insurance_provider=report_output.get("insurance_provider", "unknown"),
            hospital_name=report_output.get("hospital_name", "unknown"),
            address=report_output.get("address", "unknown"),
            emergency_contact=report_output.get("emergency_contact", "unknown"),
            distance_km=report_output.get("distance_km", "unknown"),
            assigned_doctor_name=assigned_doctor.get("name", "Not assigned"),
            assigned_doctor_title=assigned_doctor.get("title", "N/A"),
            loa_number=report_output.get("loa_number", "unknown"),
            date_issued=report_output.get("date_issued", "unknown"),
            valid_until=report_output.get("valid_until", "unknown"),
            approved_services=", ".join(report_output.get("approved_services", [])),
            room_type=report_output.get("room_type", "unknown"),
            exclusions=", ".join(report_output.get("exclusions", [])),
            clinical_justification=report_output.get("clinical_justification", "Not provided"),
            remarks=report_output.get("remarks", "None"),
            case_summary=report_output.get("case_summary", "Not provided"),
            next_steps=report_output.get("next_steps", "Proceed to the emergency room."),
        )}
    ]

    logger.info("Response agent Phase 2 — calling LLM...")

    response = await call_llm(messages=messages)
    return response.choices[0].message.content or "Your authorization is ready. Please proceed to the facility."


async def response_agent_node(state: AgentState) -> AgentState:
    """
    Response agent node.
    Phase 1 — no report_output yet: present top 3 hospitals, give first aid guidance.
    Phase 2 — report_output present: relay final confirmation to patient.
    """
    logger.info("="*30)
    logger.info("Response Agent Node")
    logger.info("="*30)

    report_output = state.get("report_output")
    is_phase2 = report_output is not None and report_output.get("generated", False)

    if is_phase2:
        response = await _handle_phase2(state, report_output)
    else:
        response = await _handle_phase1(state)

    logger.info("Response agent message: \n%s", response)

    return {
        "messages": [AIMessage(content=response, name="response_agent")],
        "next_agent": "END"
    }
