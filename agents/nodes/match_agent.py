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


# ── Capability Scoring ────────────────────────────────────────────────────────

def _score_hospital(hospital: dict, classification_type: str) -> int:
    """
    Returns preferred capability score for tie-breaking.
    Required capability filtering is handled separately via LLM-selected services.
    """
    caps = EMERGENCY_LOA_SERVICES_MAP.get(classification_type, EMERGENCY_LOA_SERVICES_MAP["GENERAL"])
    hospital_caps = hospital["capabilities"]
    return sum(1 for cap in caps["preferred"] if hospital_caps.get(cap, False))


# ── Match Agent Node ──────────────────────────────────────────────────────────

async def match_agent_node(state: AgentState) -> AgentState:
    """
    Match agent node — pure logic, no LLM call.
    Filters hospitals by insurance and capability, ranks by distance and score.
    """
    logger.info("="*30)
    logger.info("Match Agent Node")
    logger.info("="*30)

    ca_output = state["classification_agent_output"]
    classification_type = ca_output.get("classification_type", "GENERAL")
    location = ca_output.get("location", "unknown")
    insurance_provider = ca_output.get("insurance_provider", "unknown")
    symptoms = ca_output.get("symptoms", state["symptoms"])
    current_situation = state.get("current_situation") or "Not provided"

    # ── LLM Call: Select required services from LOA map ───────────────────────
    loa_services = EMERGENCY_LOA_SERVICES_MAP.get(
        classification_type,
        EMERGENCY_LOA_SERVICES_MAP["GENERAL"]
    )

    # Pass ALL labels to the LLM regardless of requires value
    all_labels = [svc["label"] for svc in loa_services["services"]]

    messages = [
        {"role": "system", "content": ma_prompts.SERVICES_SELECTION_SYSTEM_PROMPT},
        {"role": "user", "content": ma_prompts.SERVICES_SELECTION_QUERY_PROMPT.format(
            classification_type=classification_type,
            symptoms=symptoms,
            current_situation=current_situation,
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
                        }
                    },
                    "required": ["selected_services"],
                },
            },
        }
    )

    raw_content = response.choices[0].message.content or ""

    try:
        parsed = json.loads(raw_content)

        # Sanitize — only allow labels that exist in the map
        valid_labels = set(all_labels)
        selected_labels = [s for s in parsed["selected_services"] if s in valid_labels]

        if not selected_labels:
            logger.warning("LLM returned no valid labels, falling back to all services.")
            selected_labels = all_labels

    except json.JSONDecodeError as e:
        logger.error("Failed to parse services selection: %s | Raw: %s", e, raw_content)
        selected_labels = all_labels  # fallback: use all services

    logger.info("LLM selected service labels: %s", selected_labels)

    # ── Back-map labels → requires keys for hospital capability checking ───────
    # Build a label→requires lookup from the map
    label_to_requires = {
        svc["label"]: svc["requires"]
        for svc in loa_services["services"]
    }

    # Extract only the capability keys we need to check (excludes None)
    required_capability_keys = [
        label_to_requires[label]
        for label in selected_labels
        if label_to_requires.get(label) is not None
    ]

    logger.info("Required capability keys for hospital filter: %s", required_capability_keys)


    # ── Step 1: Get patient coordinates ───────────────────────────────────────
    patient_lat, patient_lng = _get_patient_coordinates(location)
    logger.info("Patient coordinates: %s, %s", patient_lat, patient_lng)

    # ── Step 2: Filter by insurance ───────────────────────────────────────────
    insurance_filtered = [
        h for h in HOSPITALS
        if insurance_provider in h["insurance_accepted"]
    ]
    logger.info("Hospitals after insurance filter: %s", len(insurance_filtered))
    hospital_id_left = []
    for hospital in insurance_filtered:
        hospital_id_left.append(hospital.get("id"))
    logger.info("Hospital IDs Left: %s", hospital_id_left)

    # ── Step 3: Filter by classification type + required capability keys ──────
    capable_hospitals = []
    for hospital in insurance_filtered:
        if classification_type not in hospital["emergency_types_supported"]:
            continue

        hospital_caps = hospital["capabilities"]
        has_all = all(hospital_caps.get(cap, False) for cap in required_capability_keys)

        if has_all:
            capable_hospitals.append(hospital)

    logger.info("Hospitals after capability filter: %s", len(capable_hospitals))
    hospital_id_left = []
    for hospital in capable_hospitals:
        hospital_id_left.append(hospital.get("id"))
    logger.info("Hospital IDs Left: %s", hospital_id_left)

    # ── Step 4: Rank by distance + preferred score ────────────────────────────
    ranked = []
    for hospital in capable_hospitals:
        distance_km = _haversine_distance(
            patient_lat, patient_lng,
            hospital["lat"], hospital["lng"]
        )
        ranked.append({
            "hospital": hospital,
            "distance_km": round(distance_km, 2),
        })

    ranked.sort(key=lambda x: x["distance_km"])

    # ── Top match ─────────────────────────────────────────────────────────────
    if not ranked:
        logger.warning("No matching hospitals found.")
        match_output = {
            "matched": False,
            "no_match_reason": (
                f"No hospitals found accepting {insurance_provider} "
                f"with required services for {classification_type}."
            )
        }
    else:
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
        }

    logger.info("Match output: %s", json.dumps(
        {k: v for k, v in match_output.items() if k != "hospital_raw"}, indent=2
    ))

    return {
        "selected_loa_services": selected_labels,
        "match_agent_output": match_output,
        "next_agent": "loa_agent"
    }
