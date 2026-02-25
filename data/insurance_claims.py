"""Mock insurance claims history database for MediRoute AI hackathon."""

from datetime import date

# Mock claims history - tracks all claims made by patients within their policy period
# Each claim has a date, amount, and description
# The total of claims within the policy year is subtracted from max_benefit_limit

INSURANCE_CLAIMS_HISTORY = [
    # Juan dela Cruz - Policy MAX-2024-00123
    # Valid from: 2026-01-01 to 2027-01-01
    # Max benefit: PHP 500,000
    {
        "policy_number": "MAX-2024-00123",
        "claim_id": "CLM-2026-001",
        "claim_date": "2026-01-15",
        "claim_amount": 45000.00,
        "service_type": "Emergency Room Visit",
        "hospital": "Makati Medical Center",
        "status": "APPROVED",
        "description": "Emergency treatment for minor laceration"
    },
    {
        "policy_number": "MAX-2024-00123",
        "claim_id": "CLM-2026-002",
        "claim_date": "2026-02-03",
        "claim_amount": 125000.00,
        "service_type": "Hospitalization",
        "hospital": "St. Luke's Medical Center",
        "status": "APPROVED",
        "description": "3-day hospitalization for pneumonia treatment"
    },
    
    # Roberto Reyes - Policy INS-2024-00789
    # Valid from: 2025-03-01 to 2026-03-01
    # Max benefit: PHP 750,000
    {
        "policy_number": "INS-2024-00789",
        "claim_id": "CLM-2025-045",
        "claim_date": "2025-05-12",
        "claim_amount": 85000.00,
        "service_type": "Outpatient Surgery",
        "hospital": "Asian Hospital and Medical Center",
        "status": "APPROVED",
        "description": "Minor surgical procedure"
    },
    {
        "policy_number": "INS-2024-00789",
        "claim_id": "CLM-2025-067",
        "claim_date": "2025-08-20",
        "claim_amount": 32000.00,
        "service_type": "Laboratory Tests",
        "hospital": "The Medical City",
        "status": "APPROVED",
        "description": "Comprehensive health screening"
    },
    {
        "policy_number": "INS-2024-00789",
        "claim_id": "CLM-2025-089",
        "claim_date": "2025-11-05",
        "claim_amount": 58000.00,
        "service_type": "Emergency Room Visit",
        "hospital": "Manila Doctors Hospital",
        "status": "APPROVED",
        "description": "Emergency treatment for chest pain"
    },
    
    # Maria Santos - Policy AIA-2024-00456 (EXPIRED)
    # Valid from: 2024-06-01 to 2025-06-01
    # Max benefit: PHP 1,000,000
    # Note: This policy is expired, but claims are kept for historical records
    {
        "policy_number": "AIA-2024-00456",
        "claim_id": "CLM-2024-234",
        "claim_date": "2024-09-15",
        "claim_amount": 250000.00,
        "service_type": "Hospitalization",
        "hospital": "Philippine General Hospital",
        "status": "APPROVED",
        "description": "7-day hospitalization for dengue fever"
    },
    {
        "policy_number": "AIA-2024-00456",
        "claim_id": "CLM-2025-012",
        "claim_date": "2025-01-20",
        "claim_amount": 180000.00,
        "service_type": "Emergency Surgery",
        "hospital": "Veterans Memorial Medical Center",
        "status": "APPROVED",
        "description": "Emergency appendectomy"
    },
]


def get_claims_for_policy(policy_number: str, valid_from: str, valid_until: str) -> list[dict]:
    """
    Get all approved claims for a policy within its current validity period.
    
    Args:
        policy_number: The insurance policy number
        valid_from: Policy validity start date (ISO format: YYYY-MM-DD)
        valid_until: Policy validity end date (ISO format: YYYY-MM-DD)
    
    Returns:
        List of claim records within the policy period
    """
    from_date = date.fromisoformat(valid_from)
    until_date = date.fromisoformat(valid_until)
    
    claims = []
    for claim in INSURANCE_CLAIMS_HISTORY:
        if claim["policy_number"] != policy_number:
            continue
        
        if claim["status"] != "APPROVED":
            continue
            
        claim_date = date.fromisoformat(claim["claim_date"])
        
        # Only include claims within the current policy period
        if from_date <= claim_date <= until_date:
            claims.append(claim)
    
    return claims


def calculate_used_benefits(policy_number: str, valid_from: str, valid_until: str) -> float:
    """
    Calculate total approved claim amounts for a policy within its current validity period.
    
    Args:
        policy_number: The insurance policy number
        valid_from: Policy validity start date (ISO format: YYYY-MM-DD)
        valid_until: Policy validity end date (ISO format: YYYY-MM-DD)
    
    Returns:
        Total amount of approved claims in PHP
    """
    claims = get_claims_for_policy(policy_number, valid_from, valid_until)
    return sum(claim["claim_amount"] for claim in claims)


def calculate_remaining_benefits(
    policy_number: str, 
    max_benefit_limit: float,
    valid_from: str, 
    valid_until: str
) -> float:
    """
    Calculate remaining benefit limit for a policy.
    
    Args:
        policy_number: The insurance policy number
        max_benefit_limit: Maximum benefit limit for the policy period
        valid_from: Policy validity start date (ISO format: YYYY-MM-DD)
        valid_until: Policy validity end date (ISO format: YYYY-MM-DD)
    
    Returns:
        Remaining benefit amount in PHP
    """
    used = calculate_used_benefits(policy_number, valid_from, valid_until)
    remaining = max_benefit_limit - used
    return max(0.0, remaining)  # Cannot be negative
