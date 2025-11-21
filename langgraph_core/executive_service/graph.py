"""Minimal LangGraph definition for the executive service."""
from typing import Any, Dict, NotRequired, Optional, TypedDict

from langgraph.graph import END, StateGraph


class ExecState(TypedDict, total=False):
    """State flowing through the executive decision graph."""

    question: str
    context: Optional[Dict[str, Any]]
    decision: NotRequired[str]
    reasoning_summary: NotRequired[str]


def ceo_decider(state: ExecState) -> ExecState:
    """Stub CEO decision node.

    Replace this stub with an LLM-backed implementation that uses
    ``MODEL_URL`` and ``MODEL_NAME`` from the settings when integrating
    the real model.
    """

    question = state.get("question", "")
    decision = f"Stub decision for: {question}"
    reasoning_summary = "This is a placeholder. Integrate real LLM later."
    return {"decision": decision, "reasoning_summary": reasoning_summary}


def build_graph():
    """Build and return the compiled executive LangGraph."""

    graph = StateGraph(ExecState)
    graph.add_node("ceo_decider", ceo_decider)
    graph.set_entry_point("ceo_decider")
    graph.add_edge("ceo_decider", END)
    return graph.compile()


compiled_graph = build_graph()
