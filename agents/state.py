from typing import TypedDict, Optional


class ClassificationAgentOutput(TypedDict):
    """Output model of classification agent."""
    symptoms: str
    classification_type: str
    location: str
    insurance_provider: str


class MatchAgentOutput(TypedDict):
    """Output model of match agent."""
    matched: bool
    hospital_id: str
    hospital_name: str
    address: str
    contact: str
    emergency_contact: str
    distance_km: float
    capabilities: dict
    hospital_raw: dict
    no_match_reason: Optional[str]


class LOAOutput(TypedDict):
    """Output model of LOA agent."""
    generated: bool
    # Authorization details
    loa_number: str
    date_issued: str
    valid_until: str
    # Insurance
    insurance_provider: str
    # Patient
    symptoms: str
    classification_type: str
    current_situation: str
    # Hospital
    hospital_id: str
    hospital_name: str
    address: str
    contact: str
    emergency_contact: str
    distance_km: float
    # Coverage
    approved_services: list[str]
    room_type: str
    exclusions: list[str]
    # LLM generated
    clinical_justification: str
    remarks: str
    # Failure
    reason: Optional[str]


class ReportOutput(TypedDict):
    """Output model of report agent."""
    generated: bool
    # LLM generated
    case_summary: str
    hospital_recommendation_reason: str
    next_steps: str
    # Patient situation
    symptoms: str
    current_situation: str
    classification_type: str
    # Insurance
    insurance_provider: str
    # LOA details
    loa_number: str
    date_issued: str
    valid_until: str
    clinical_justification: str
    remarks: str
    # Hospital
    hospital_id: str
    hospital_name: str
    address: str
    contact: str
    emergency_contact: str
    distance_km: float
    # Coverage
    approved_services: list[str]
    room_type: str
    exclusions: list[str]
    # Failure
    reason: Optional[str]


class AgentState(TypedDict):
    """State of the Agents"""
    next_agent: str
    # Input fields
    symptoms: str
    location: str
    insurance: str
    current_situation: Optional[str]
    # Agent outputs
    classification_agent_output: ClassificationAgentOutput
    selected_loa_services: list[str]
    match_agent_output: MatchAgentOutput
    loa_output: LOAOutput
    report_output: ReportOutput