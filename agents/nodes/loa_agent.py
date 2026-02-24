"""LOA Agent - Creates LOA for the patient."""
import logging
import uuid
import json

from datetime import datetime, timedelta

from agents.state import AgentState
from agents.prompts import loa_agent_prompts as loa_prompts
from data.hospitals import EMERGENCY_LOA_SERVICES_MAP
from utils.llm_util import call_llm

logger = logging.getLogger(__name__)


async def loa_agent_node(state: AgentState) -> AgentState:
    """
    LOA agent node — generates a Letter of Authorization for the matched hospital.
    Deterministic fields are built from state, LLM generates only clinical_justification
    and remarks.
    """
    logger.info("=" * 30)
    logger.info("LOA Agent Node")
    logger.info("=" * 30)

    ca_output = state["classification_agent_output"]
    ma_output = state["match_agent_output"]
    selected_labels = state["selected_loa_services"]

    classification_type = ca_output.get("classification_type", "GENERAL")
    symptoms = ca_output.get("symptoms", state["symptoms"])
    insurance_provider = ca_output.get("insurance_provider", state["insurance"])
    severity = ca_output.get("severity", "URGENT")
    current_situation = state.get("current_situation") or "Not provided"
    hospital_raw = ma_output.get("hospital_raw", {})

    # ── Resolve approved services ─────────────────────────────────────────────
    # Filter selected labels against hospital capabilities
    loa_map = EMERGENCY_LOA_SERVICES_MAP.get(
        classification_type,
        EMERGENCY_LOA_SERVICES_MAP["GENERAL"]
    )

    label_to_requires = {
        svc["label"]: svc["requires"]
        for svc in loa_map["services"]
    }

    hospital_caps = hospital_raw.get("capabilities", {})

    # Include label if:
    # - requires is None (always include), OR
    # - hospital has that capability
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
            hospital_name=ma_output["hospital_name"],
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
        # Authorization details
        "loa_number": loa_number,
        "date_issued": date_issued,
        "valid_until": valid_until,
        # Insurance info
        "insurance_provider": insurance_provider,
        # Patient info
        "symptoms": symptoms,
        "classification_type": classification_type,
        "severity": severity,
        "current_situation": current_situation,
        # Hospital info
        "hospital_id": ma_output["hospital_id"],
        "hospital_name": ma_output["hospital_name"],
        "address": ma_output["address"],
        "contact": ma_output["contact"],
        "emergency_contact": ma_output["emergency_contact"],
        "distance_km": ma_output["distance_km"],
        # Coverage details
        "approved_services": approved_services,
        "room_type": room_type,
        "exclusions": exclusions,
        # LLM-generated fields
        "clinical_justification": clinical_justification,
        "remarks": remarks,
    }

    logger.info("LOA generated: %s", loa_number)
    logger.info("LOA output: %s", json.dumps(
        {k: v for k, v in loa_output.items()}, indent=2
    ))

    return {
        "loa_output": loa_output,
        "next_agent": "report_agent"
    }
