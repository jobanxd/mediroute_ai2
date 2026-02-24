from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages


class ClassificationAgentOutput(TypedDict):
    """Output model of classification agent."""
    symptoms: str
    classification_type: str
    severity: str
    recommended_action: str
    confidence: str
    classification_rationale: str
    dispatch_required: bool
    dispatch_rationale: str
    location: str
    insurance_provider: str
    preferred_hospital: str


class MatchAgentAutoSelectedOutput(TypedDict):
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


class HospitalOption(TypedDict):
    hospital_id: str
    hospital_name: str
    address: str
    contact: str
    emergency_contact: str
    distance_km: float


class MatchTop3Output(TypedDict):
    matched: bool
    top_hospitals: list[HospitalOption]
    preferred_hospital_used: bool
    auto_selected: bool


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
    severity: str
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
    assigned_doctor = Optional[str]


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
    severity: str
    recommended_action: str
    dispatch_required: bool
    dispatch_rationale: str
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
    assigned_doctor_name: str
    assigned_doctor_title: str
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
    messages: Annotated[list, add_messages]
    next_agent: str
    # Agent outputs
    classification_agent_output: ClassificationAgentOutput
    selected_loa_services: list[str]
    match_agent_output: MatchAgentAutoSelectedOutput | MatchTop3Output
    chosen_hospital: Optional[str]
    loa_output: LOAOutput
    report_output: ReportOutput