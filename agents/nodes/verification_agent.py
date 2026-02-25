"""Verification agent node — verifies patient identity and insurance eligibility."""
import logging

from datetime import date
from langchain_core.messages import AIMessage

from agents.state import AgentState
from data.insurance import INSURANCE_RECORDS
from data.insurance_claims import (
    get_claims_for_policy,
    calculate_used_benefits,
    calculate_remaining_benefits
)
from utils.llm_util import call_llm

logger = logging.getLogger(__name__)


def get_insurance_record(full_name: str) -> dict | None:
    """
    Mock DB lookup — finds insurance record by full name (case-insensitive).
    In production: replace with a parameterized SQL query against your policy table.

    Example SQL equivalent:
        SELECT * FROM insurance_policies
        WHERE LOWER(full_name) = LOWER(:full_name)
        AND status = 'ACTIVE'
        LIMIT 1;
    """
    return next(
        (r for r in INSURANCE_RECORDS if r["full_name"].lower() == full_name.lower()),
        None
    )


def check_insurance_validity(record: dict) -> tuple[bool, str]:
    """
    Checks if the insurance policy is currently valid.
    Returns (is_valid, reason).
    """
    if record["status"] != "ACTIVE":
        return False, f"Policy is {record['status'].lower()}"

    valid_until = date.fromisoformat(record["valid_until"])
    if date.today() > valid_until:
        return False, f"Policy expired on {record['valid_until']}"

    return True, "Policy is active and valid"


async def verification_agent_node(state: AgentState) -> AgentState:
    """
    Verification agent node — looks up the patient's insurance record
    by full name and validates eligibility before routing to classification.

    In production: get_insurance_record() queries a relational DB.
    For the hackathon: returns mock data directly.
    """
    logger.info("="*30)
    logger.info("Verification Agent Node")
    logger.info("="*30)

    state_messages = state.get("messages", [])
    patient_name = state.get("patient_name", "").strip()

    logger.info("Looking up insurance record for: %s", patient_name)

    # ── DB Lookup (mock) ──────────────────────────────────────────────────────
    record = get_insurance_record(patient_name)

    if not record:
        logger.warning("No insurance record found for: %s", patient_name)

        summary = (
            f"Verification failed: no insurance record found for '{patient_name}' "
            f"in the system. The patient may not be registered or the name may not match."
        )

        return {
            "messages": [AIMessage(content=summary, name="verification_agent")],
            "verification_output": {
                "verified": False,
                "reason": f"No insurance record found for '{patient_name}'.",
            },
            "next_agent": "response_agent"
        }

    # ── Validity Check ────────────────────────────────────────────────────────
    is_valid, validity_reason = check_insurance_validity(record)

    if not is_valid:
        logger.warning(
            "Insurance record found for '%s' but is not valid: %s",
            patient_name, validity_reason
        )

        summary = (
            f"Verification failed for '{patient_name}'. "
            f"Policy {record['policy_number']} ({record['insurance_provider']} — {record['plan_name']}) "
            f"is not currently valid: {validity_reason}."
        )

        return {
            "messages": [AIMessage(content=summary, name="verification_agent")],
            "verification_output": {
                "verified": False,
                "reason": validity_reason,
                "policy_number": record["policy_number"],
                "insurance_provider": record["insurance_provider"],
                "plan_name": record["plan_name"],
                "status": record["status"],
            },
            "next_agent": "response_agent"
        }

    # ── Verified ──────────────────────────────────────────────────────────────
    logger.info(
        "Insurance verified for '%s' — Policy: %s | Provider: %s | Valid until: %s",
        patient_name,
        record["policy_number"],
        record["insurance_provider"],
        record["valid_until"],
    )

    # ── Calculate Benefit Usage ───────────────────────────────────────────────
    policy_number = record["policy_number"]
    valid_from = record["valid_from"]
    valid_until = record["valid_until"]
    max_benefit = record["max_benefit_limit"]
    
    # Get claims history within the current policy period
    claims_history = get_claims_for_policy(policy_number, valid_from, valid_until)
    used_benefits = calculate_used_benefits(policy_number, valid_from, valid_until)
    remaining_benefits = calculate_remaining_benefits(policy_number, max_benefit, valid_from, valid_until)
    
    logger.info(
        "Benefit tracking for policy %s: Used: PHP %,.2f | Remaining: PHP %,.2f | Claims count: %d",
        policy_number,
        used_benefits,
        remaining_benefits,
        len(claims_history)
    )

    original_query = next(
        (m.content for m in reversed(state_messages)
         if isinstance(m, AIMessage) and m.name == "orchestrator_agent"),
        "No query found."
    )

    summary = (
        f"Insurance verified for {record['full_name']}. "
        f"Policy {record['policy_number']} under {record['insurance_provider']} "
        f"({record['plan_name']}) is active and valid until {record['valid_until']}. "
        f"Coverage type: {record['coverage_type']}. "
        f"Max benefit limit: PHP {record['max_benefit_limit']:,.2f}. "
        f"Used benefits: PHP {used_benefits:,.2f}. "
        f"Remaining benefits: PHP {remaining_benefits:,.2f} ({len(claims_history)} claim(s) this period). "
        f"Verification passed. Forwarding the following request to classification: "
        f"\"{original_query}\""
    )

    logger.info("Verification summary: %s", summary)

    return {
        "messages": [AIMessage(content=summary, name="verification_agent")],
        "verification_output": {
            "verified": True,
            "policy_number": record["policy_number"],
            "full_name": record["full_name"],
            "date_of_birth": record["date_of_birth"],
            "insurance_provider": record["insurance_provider"],
            "plan_name": record["plan_name"],
            "plan_type": record["plan_type"],
            "coverage_type": record["coverage_type"],
            "valid_from": record["valid_from"],
            "valid_until": record["valid_until"],
            "max_benefit_limit": record["max_benefit_limit"],
            "room_and_board_limit": record["room_and_board_limit"],
            "dependents": record["dependents"],
            "status": record["status"],
            "used_benefits": used_benefits,
            "remaining_benefits": remaining_benefits,
            "claims_history": claims_history,
        },
        "next_agent": "classification_agent"
    }