"""LOA Agent - Creates LOA for the patient."""
import logging
import uuid
import json

from datetime import datetime, timedelta
from langchain_core.messages import AIMessage

from agents.state import AgentState
from agents.prompts import loa_agent_prompts as loa_prompts
from data.hospitals import HOSPITALS, EMERGENCY_LOA_SERVICES_MAP
from utils.llm_util import call_llm

logger = logging.getLogger(__name__)


async def loa_agent_node(state: AgentState) -> AgentState:
    """
    LOA agent node — generates a Letter of Authorization for the matched hospital.

    Handles 3 scenarios:
    1. Preferred hospital passed checks → hospital_raw already in match_agent_output
    2. CRITICAL auto-select → hospital_raw already in match_agent_output
    3. User chose from top 3 → resolve hospital_raw from chosen_hospital in state
    """
    logger.info("=" * 30)
    logger.info("LOA Agent Node")
    logger.info("=" * 30)

    ca_output = state["classification_agent_output"]
    ma_output = state["match_agent_output"]
    selected_labels = state["selected_loa_services"]
    chosen_hospital = state.get("chosen_hospital")

    classification_type = ca_output.get("classification_type", "GENERAL")
    symptoms = ca_output.get("symptoms", state.get("symptoms", "unknown"))
    insurance_provider = ca_output.get("insurance_provider", state.get("insurance", "unknown"))
    severity = ca_output.get("severity", "URGENT")
    current_situation = state.get("current_situation") or "Not provided"

    # ── Resolve hospital_raw ───────────────────────────────────────────────────
    # Scenario 1 & 2: hospital_raw is already in match_agent_output
    # Scenario 3: user chose from top 3 — resolve from chosen_hospital name
    hospital_raw = ma_output.get("hospital_raw")

    if not hospital_raw:
        # Scenario 3 — user selected from top 3
        if not chosen_hospital:
            logger.error("No hospital_raw in match output and no chosen_hospital in state.")
            return {
                "loa_output": {
                    "generated": False,
                    "reason": "Unable to determine selected hospital. No hospital_raw or chosen_hospital found."
                },
                "next_agent": "end"
            }

        logger.info("Resolving hospital_raw from chosen_hospital: %s", chosen_hospital)

        hospital_raw = next(
            (h for h in HOSPITALS if h["name"].lower() == chosen_hospital.lower()),
            None
        )

        if not hospital_raw:
            logger.error("Chosen hospital '%s' not found in registry.", chosen_hospital)
            return {
                "loa_output": {
                    "generated": False,
                    "reason": f"Chosen hospital '{chosen_hospital}' could not be found in the hospital registry."
                },
                "next_agent": "end"
            }

        # Also resolve distance_km from top_hospitals list if available
        top_hospitals = ma_output.get("top_hospitals", [])
        matched_top = next(
            (h for h in top_hospitals if h["hospital_name"].lower() == chosen_hospital.lower()),
            None
        )

        # Build a resolved ma_output so the rest of the node works uniformly
        resolved_hospital_details = matched_top or {}
        hospital_name = hospital_raw["name"]
        hospital_id = hospital_raw["id"]
        address = hospital_raw["address"]
        contact = hospital_raw["contact"]
        emergency_contact = hospital_raw["emergency_contact"]
        distance_km = resolved_hospital_details.get("distance_km", ma_output.get("distance_km", 0.0))

        logger.info("Resolved hospital from user selection: %s", hospital_name)

    else:
        # Scenario 1 & 2 — hospital_raw already present
        hospital_name = ma_output["hospital_name"]
        hospital_id = ma_output["hospital_id"]
        address = ma_output["address"]
        contact = ma_output["contact"]
        emergency_contact = ma_output["emergency_contact"]
        distance_km = ma_output["distance_km"]

        logger.info(
            "Hospital resolved from match_agent_output (%s): %s",
            "preferred" if ma_output.get("preferred_hospital_used") else "auto-selected",
            hospital_name
        )

    # ── Resolve approved services ─────────────────────────────────────────────
    loa_map = EMERGENCY_LOA_SERVICES_MAP.get(
        classification_type,
        EMERGENCY_LOA_SERVICES_MAP["GENERAL"]
    )

    label_to_requires = {
        svc["label"]: svc["requires"]
        for svc in loa_map["services"]
    }

    hospital_caps = hospital_raw.get("capabilities", {})

    approved_services = [
        label for label in selected_labels
        if label_to_requires.get(label) is None
        or hospital_caps.get(label_to_requires[label], False)
    ]

    room_type = loa_map["room_type"]
    exclusions = loa_map["typical_exclusions"]

    logger.info("Approved services: %s", approved_services)

    # ── LLM Call: clinical_justification + remarks ────────────────────────────
    messages = [
        {"role": "system", "content": loa_prompts.LOA_SYSTEM_PROMPT},
        {"role": "user", "content": loa_prompts.LOA_QUERY_PROMPT.format(
            symptoms=symptoms,
            current_situation=current_situation,
            classification_type=classification_type,
            severity=severity,
            insurance_provider=insurance_provider,
            hospital_name=hospital_name,
            approved_services=json.dumps(approved_services, indent=2),
        )}
    ]

    logger.info("Calling LLM for clinical justification and remarks...")

    response = await call_llm(
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "loa_soft_fields",
                "schema": {
                    "type": "object",
                    "properties": {
                        "clinical_justification": {"type": "string"},
                        "remarks": {"type": "string"},
                    },
                    "required": ["clinical_justification", "remarks"],
                },
            },
        }
    )

    raw_content = response.choices[0].message.content or ""

    try:
        soft_fields = json.loads(raw_content)
        clinical_justification = soft_fields.get("clinical_justification", "")
        remarks = soft_fields.get("remarks", "")
    except json.JSONDecodeError as e:
        logger.error("Failed to parse LOA soft fields: %s | Raw: %s", e, raw_content)
        clinical_justification = (
            f"Patient presents with {symptoms} requiring {classification_type} "
            f"emergency admission and treatment."
        )
        remarks = "Please prioritize emergency assessment upon arrival."

    # ── Build deterministic LOA fields ────────────────────────────────────────
    now = datetime.now()
    loa_number = f"LOA-{now.strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    date_issued = now.strftime("%B %d, %Y %I:%M %p")
    valid_until = (now + timedelta(hours=48)).strftime("%B %d, %Y %I:%M %p")

    # ── Assemble full LOA ─────────────────────────────────────────────────────
    loa_output = {
        "generated": True,
        "loa_number": loa_number,
        "date_issued": date_issued,
        "valid_until": valid_until,
        "insurance_provider": insurance_provider,
        "symptoms": symptoms,
        "classification_type": classification_type,
        "severity": severity,
        "current_situation": current_situation,
        "hospital_id": hospital_id,
        "hospital_name": hospital_name,
        "address": address,
        "contact": contact,
        "emergency_contact": emergency_contact,
        "distance_km": distance_km,
        "approved_services": approved_services,
        "room_type": room_type,
        "exclusions": exclusions,
        "clinical_justification": clinical_justification,
        "remarks": remarks,
    }

    logger.info("LOA generated: %s", loa_number)
    logger.info("LOA output: %s", json.dumps(loa_output, indent=2))

    # ── Build LOA summary message ─────────────────────────────────────────────
    summary = (
        f"LOA Created — {loa_number}\n"
        f"Issued: {date_issued} | Valid Until: {valid_until}\n\n"
        f"Patient: {symptoms} ({classification_type} | {severity})\n"
        f"Insurance: {insurance_provider}\n\n"
        f"Hospital: {hospital_name}\n"
        f"Address: {address}\n"
        f"Emergency Contact: {emergency_contact} | Distance: {distance_km} km\n\n"
        f"Approved Services: {', '.join(approved_services)}\n"
        f"Room Type: {room_type}\n"
        f"Exclusions: {', '.join(exclusions) if exclusions else 'None'}\n\n"
        f"Clinical Justification: {clinical_justification}\n"
        f"Remarks: {remarks}"
    )

    logger.info("LOA summary message: \n%s", summary)

    return {
        "messages": [AIMessage(content=summary, name="loa_agent")],
        "loa_output": loa_output,
        "next_agent": "report_agent"
    }
