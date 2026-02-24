"""MediRoute AI - LangGraph Graph Definition"""
from langgraph.graph import StateGraph, START, END

from agents.state import AgentState
from agents.nodes.orchestrator_agent import orchestrator_agent_node
from agents.nodes.classification_agent import classification_agent_node
from agents.nodes.match_agent import match_agent_node
from agents.nodes.loa_agent import loa_agent_node
from agents.nodes.report_agent import report_agent_node
from agents.nodes.response_agent import response_agent_node


async def _get_routing_decision(state: AgentState) -> str:
    """Reads next_agent from state to determine routing."""
    return state["next_agent"]


# ── Build Graph ────────────────────────────────────────────────
builder = StateGraph(AgentState)

# ── Nodes ─────────────────────────────────────────────────────
builder.add_node("orchestrator_agent", orchestrator_agent_node)
builder.add_node("classification_agent", classification_agent_node)
builder.add_node("match_agent", match_agent_node)
builder.add_node("loa_agent", loa_agent_node)
builder.add_node("report_agent", report_agent_node)
builder.add_node("response_agent", response_agent_node)

# ── Edges ────────────────────────────────────────────────
builder.add_edge(START, "orchestrator_agent")

# First Phase
builder.add_edge("classification_agent", "match_agent")

# Second Phase
builder.add_edge("loa_agent", "report_agent")
builder.add_edge("report_agent", "response_agent")

# Terminal
builder.add_edge("response_agent", END)

# Orchestrator either answers directly (FINISH) or routes to intake
builder.add_conditional_edges(
    "orchestrator_agent",
    _get_routing_decision,
    {
        "orchestrator_agent": END,   # direct answer, no emergency detected
        "classification_agent": "classification_agent",
        "loa_agent": "loa_agent"
    }
)

builder.add_conditional_edges(
    "match_agent",
    _get_routing_decision,
    {
        "response_agent": "response_agent",
        "loa_agent": "loa_agent",
    }
)

graph = builder.compile()
