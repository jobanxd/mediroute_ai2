"""MediRoute AI - LangGraph Graph Definition"""
from langgraph.graph import StateGraph, START, END

from agents.state import AgentState
from agents.nodes.classification_agent import classification_agent_node
from agents.nodes.match_agent import match_agent_node
from agents.nodes.loa_agent import loa_agent_node
from agents.nodes.report_agent import report_agent_node


# ── Build Graph ────────────────────────────────────────────────
builder = StateGraph(AgentState)

# ── Nodes ─────────────────────────────────────────────────────
builder.add_node("classification_agent", classification_agent_node)
builder.add_node("match_agent", match_agent_node)
builder.add_node("loa_agent", loa_agent_node)
builder.add_node("report_agent", report_agent_node)

# ── Edges ─────────────────────────────────────────────────────
builder.add_edge(START, "classification_agent")
builder.add_edge("classification_agent", "match_agent")
builder.add_edge("match_agent", "loa_agent")
builder.add_edge("loa_agent", "report_agent")
builder.add_edge("report_agent", END)

graph = builder.compile()
