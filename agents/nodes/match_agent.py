"""Match agent node — filters and ranks hospitals by insurance, capability, and distance."""
import logging
import json
from math import radians, sin, cos, sqrt, atan2

from langchain_core.messages import AIMessage

from agents.state import AgentState
from agents.prompts import match_agent_prompts as ma_prompts
from data.hospitals import HOSPITALS, EMERGENCY_LOA_SERVICES_MAP
from utils.llm_util import call_llm

logger = logging.getLogger(__name__)


# ── Haversine Distance ────────────────────────────────────────────────────────

def _haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance in km between two coordinates."""
    r = 6371  # Earth radius in km
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    return r * 2 * atan2(sqrt(a), sqrt(1 - a))


# ── Geocoding (mock) ──────────────────────────────────────────────────────────

def _get_patient_coordinates(location: str) -> tuple:
    """
    Mock geocoding — maps known PH locations to lat/lng.
    In production replace with Nominatim or Google Maps API.
    """
    location_lower = location.lower()

    location_map = {
        "bgc": (14.5494, 121.0509),
        "bonifacio global city": (14.5494, 121.0509),
        "taguig": (14.5243, 121.0792),
        "makati": (14.5547, 121.0244),
        "ortigas": (14.5872, 121.0674),
        "pasig": (14.5764, 121.0851),
        "quezon city": (14.6760, 121.0437),
        "qc": (14.6760, 121.0437),
        "manila": (14.5995, 120.9842),
        "malate": (14.5649, 120.9904),
        "ermita": (14.5831, 120.9794),
        "alabang": (14.4195, 121.0347),
        "muntinlupa": (14.4081, 121.0415),
        "san juan": (14.5997, 121.0382),
        "greenhills": (14.5997, 121.0382),
        "mandaluyong": (14.5794, 121.0359),
    }

    for key, coords in location_map.items():
        if key in location_lower:
            return coords

    # Default to Metro Manila center if location not recognized
    logger.warning("Location not recognized: %s - defaulting to Metro Manila center", location)
    return (14.5995, 120.9842)

async def _summarize_match(
    classification_type: str,
    severity: str,
    location: str,
    insurance_provider: str,
    preferred_hospital: str | None,
    selected_labels: list,
    match_output: dict,
    next_agent: str,
) -> str:
    summary_messages = [
        {"role": "system", "content": ma_prompts.MATCH_SUMMARY_SYSTEM_PROMPT},
        {"role": "user", "content": ma_prompts.MATCH_SUMMARY_QUERY_PROMPT.format(
            classification_type=classification_type,
            severity=severity,
            location=location,
            insurance_provider=insurance_provider,
            preferred_hospital=preferred_hospital or "None",
            selected_loa_services=", ".join(selected_labels),
            match_output=json.dumps(
                {k: v for k, v in match_output.items() if k != "hospital_raw"},
                indent=2
            ),
            next_agent=next_agent,
        )}
    ]

    summary_response = await call_llm(messages=summary_messages)
    return summary_response.choices[0].message.content or "Hospital matching complete."

# ── Match Agent Node ──────────────────────────────────────────────────────────

async def match_agent_node(state: AgentState) -> AgentState:
    """
    Match agent node — Filters hospitals by insurance and capability, ranks by distance.
    """
    logger.info("="*30)
    logger.info("Match Agent Node")
    logger.info("="*30)

    ca_output = state["classification_agent_output"]
    classification_type = ca_output.get("classification_type", "GENERAL")
    location = ca_output.get("location", "unknown")
    insurance_provider = ca_output.get("insurance_provider", "unknown")
    symptoms = ca_output.get("symptoms")
    severity = ca_output.get("severity", "URGENT")
    recommended_action = ca_output.get("recommended_action", "HOSPITAL_ADMISSION")
    preferred_hospital = ca_output.get("preferred_hospital")  # may be None

    # ── LLM Call: Select required services from LOA map ───────────────────────
    loa_services = EMERGENCY_LOA_SERVICES_MAP.get(
        classification_type,
        EMERGENCY_LOA_SERVICES_MAP["GENERAL"]
    )

    all_labels = [svc["label"] for svc in loa_services["services"]]

    messages = [
        {"role": "system", "content": ma_prompts.SERVICES_SELECTION_SYSTEM_PROMPT},
        {"role": "user", "content": ma_prompts.SERVICES_SELECTION_QUERY_PROMPT.format(
            classification_type=classification_type,
            severity=severity,
            symptoms=symptoms,
            recommended_action=recommended_action,
            available_services=json.dumps(all_labels, indent=2),
        )}
    ]

    logger.info("Calling LLM for services selection...")

    response = await call_llm(
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "services_selection",
                "schema": {
                    "type": "object",
                    "properties": {
                        "selected_services": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "services_rationale": {
                            "type": "string",
                            "description": "One sentence explaining the selection logic based on symptoms and severity"
                        }
                    },
                    "required": ["selected_services", "services_rationale"],
                },
            },
        }
    )

    raw_content = response.choices[0].message.content or ""

    try:
        parsed = json.loads(raw_content)
        valid_labels = set(all_labels)
        selected_labels = [s for s in parsed["selected_services"] if s in valid_labels]
        if not selected_labels:
            logger.warning("LLM returned no valid labels, falling back to all services.")
            selected_labels = all_labels
    except json.JSONDecodeError as e:
        logger.error("Failed to parse services selection: %s | Raw: %s", e, raw_content)
        selected_labels = all_labels

    logger.info("LLM selected service labels: %s", selected_labels)

    # ── Back-map labels → requires keys ───────────────────────────────────────
    label_to_requires = {
        svc["label"]: svc["requires"]
        for svc in loa_services["services"]
    }

    required_capability_keys = [
        label_to_requires[label]
        for label in selected_labels
        if label_to_requires.get(label) is not None
    ]

    logger.info("Required capability keys for hospital filter: %s", required_capability_keys)

    # ── Step 1: Get patient coordinates ───────────────────────────────────────
    patient_lat, patient_lng = _get_patient_coordinates(location)
    logger.info("Patient coordinates: %s, %s", patient_lat, patient_lng)

    # ── Helper: Check if a hospital passes insurance + capability checks ───────
    def passes_checks(hospital: dict) -> tuple[bool, str | None]:
        """Returns (passed, fail_reason). fail_reason is None if passed."""
        if insurance_provider not in hospital["insurance_accepted"]:
            return False, f"does not accept {insurance_provider} insurance"

        if classification_type not in hospital["emergency_types_supported"]:
            return False, f"does not support {classification_type} emergencies"

        hospital_caps = hospital["capabilities"]
        missing_caps = [
            cap for cap in required_capability_keys
            if not hospital_caps.get(cap, False)
        ]
        if missing_caps:
            return False, f"missing required capabilities: {', '.join(missing_caps)}"

        return True, None

    # ── Step 2: Check preferred hospital first (if provided) ──────────────────
    fail_reason = None  # initialize so it's always defined for downstream steps

    if preferred_hospital:
        logger.info("Preferred hospital requested: %s", preferred_hospital)

        preferred_match = next(
            (h for h in HOSPITALS if h["name"].lower() == preferred_hospital.lower()),
            None
        )

        if not preferred_match:
            fail_reason = "not found in the hospital registry"
            logger.warning(
                "Preferred hospital '%s' — %s. Falling back to ranked search.",
                preferred_hospital, fail_reason
            )
        else:
            passed, fail_reason = passes_checks(preferred_match)

            if passed:
                logger.info("Preferred hospital passed all checks — routing directly to LOA agent.")

                distance_km = round(_haversine_distance(
                    patient_lat, patient_lng,
                    preferred_match["lat"], preferred_match["lng"]
                ), 2)

                match_output = {
                    "matched": True,
                    "hospital_id": preferred_match["id"],
                    "hospital_name": preferred_match["name"],
                    "address": preferred_match["address"],
                    "contact": preferred_match["contact"],
                    "emergency_contact": preferred_match["emergency_contact"],
                    "distance_km": distance_km,
                    "capabilities": preferred_match["capabilities"],
                    "hospital_raw": preferred_match,
                    "preferred_hospital_used": True,
                }
                next_agent = "loa_agent"

                logger.info("Match output (preferred): %s", json.dumps(
                    {k: v for k, v in match_output.items() if k != "hospital_raw"}, indent=2
                ))

                summary = await _summarize_match(
                    classification_type, severity, location, insurance_provider,
                    preferred_hospital, selected_labels, match_output, next_agent
                )
                logger.info("Match summary: %s", summary)

                return {
                    "messages": [AIMessage(content=summary, name="match_agent")],
                    "selected_loa_services": selected_labels,
                    "match_agent_output": match_output,
                    "next_agent": next_agent
                }
            else:
                logger.warning(
                    "Preferred hospital '%s' failed checks — %s. Falling back to ranked search.",
                    preferred_hospital, fail_reason
                )

    # ── Step 3: Filter all hospitals by insurance + capability ────────────────
    capable_hospitals = [h for h in HOSPITALS if passes_checks(h)[0]]  # unpack tuple, take bool only

    logger.info("Hospitals after insurance + capability filter: %s", len(capable_hospitals))

    # ── Step 4: Rank by distance ───────────────────────────────────────────────
    ranked = sorted(
        [
            {
                "hospital": h,
                "distance_km": round(_haversine_distance(
                    patient_lat, patient_lng, h["lat"], h["lng"]
                ), 2)
            }
            for h in capable_hospitals
        ],
        key=lambda x: x["distance_km"]
    )

    # ── Step 5: No hospitals found ────────────────────────────────────────────
    if not ranked:
        logger.warning("No matching hospitals found.")

        match_output = {
            "matched": False,
            "top_hospitals": [],
            "preferred_hospital_fail_reason": fail_reason,
            "preferred_hospital_used": False,
            "auto_selected": False,
        }
        next_agent = "END"

        summary = await _summarize_match(
            classification_type, severity, location, insurance_provider,
            preferred_hospital, selected_labels, match_output, next_agent
        )
        logger.info("Match summary: %s", summary)

        return {
            "messages": [AIMessage(content=summary, name="match_agent")],
            "selected_loa_services": selected_labels,
            "match_agent_output": match_output,
            "next_agent": next_agent
        }

    # ── Step 6: CRITICAL severity — auto-select top 1 ─────────────────────────
    if severity == "CRITICAL":
        logger.info("Severity is CRITICAL — auto-selecting top hospital.")

        top = ranked[0]
        match_output = {
            "matched": True,
            "hospital_id": top["hospital"]["id"],
            "hospital_name": top["hospital"]["name"],
            "address": top["hospital"]["address"],
            "contact": top["hospital"]["contact"],
            "emergency_contact": top["hospital"]["emergency_contact"],
            "distance_km": top["distance_km"],
            "capabilities": top["hospital"]["capabilities"],
            "hospital_raw": top["hospital"],
            "preferred_hospital_used": False,
            "auto_selected": True,
        }
        next_agent = "loa_agent"

        logger.info("Match output (critical auto-select): %s", json.dumps(
            {k: v for k, v in match_output.items() if k != "hospital_raw"}, indent=2
        ))

        summary = await _summarize_match(
            classification_type, severity, location, insurance_provider,
            preferred_hospital, selected_labels, match_output, next_agent
        )
        logger.info("Match summary: %s", summary)

        return {
            "messages": [AIMessage(content=summary, name="match_agent")],
            "selected_loa_services": selected_labels,
            "match_agent_output": match_output,
            "next_agent": next_agent
        }

    # ── Step 7: Non-critical — return top 3 for user to choose ────────────────
    logger.info("Severity is %s — returning top 3 hospitals for user selection.", severity)

    top_3 = [
        {
            "hospital_id": r["hospital"]["id"],
            "hospital_name": r["hospital"]["name"],
            "address": r["hospital"]["address"],
            "contact": r["hospital"]["contact"],
            "emergency_contact": r["hospital"]["emergency_contact"],
            "distance_km": r["distance_km"],
        }
        for r in ranked[:3]
    ]

    match_output = {
        "matched": True,
        "top_hospitals": top_3,
        "preferred_hospital_fail_reason": fail_reason,
        "preferred_hospital_used": False,
        "auto_selected": False,
    }
    next_agent = "response_agent"

    logger.info("Match output (top 3): %s", json.dumps(match_output, indent=2))

    summary = await _summarize_match(
        classification_type, severity, location, insurance_provider,
        preferred_hospital, selected_labels, match_output, next_agent
    )
    logger.info("Match summary: %s", summary)

    return {
        "messages": [AIMessage(content=summary, name="match_agent")],
        "selected_loa_services": selected_labels,
        "match_agent_output": match_output,
        "next_agent": next_agent
    }
