"""Simple mission orchestration graph for SOD-EMUNA agents.

Dependencies:
- The graph runner can be replaced with `langgraph` if available. The backend
  already lists `langgraph` in `backend/requirements.txt`; ensure it is
  installed for production deployments.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List

from app.agents.protocols import AgentRequest, AgentResponse
from app.agents.registry import AGENTS

StepHandler = Callable[["FlowContext"], Awaitable["FlowContext"]]


@dataclass
class FlowContext:
    """State container propagated through the mission graph."""

    mission_type: str
    user_id: str | int
    payload: Dict[str, Any]
    primary_agent: str
    analysis: Dict[str, Any] = field(default_factory=dict)
    plan: Dict[str, Any] = field(default_factory=dict)
    execution: Dict[str, Any] = field(default_factory=dict)
    final_message: str | None = None
    history: List[Dict[str, Any]] = field(default_factory=list)
    results: Dict[str, AgentResponse] = field(default_factory=dict)


@dataclass
class GraphNode:
    """A single node within the mission graph."""

    name: str
    handler: StepHandler

    async def __call__(self, context: FlowContext) -> FlowContext:  # pragma: no cover - thin wrapper
        return await self.handler(context)


class SimpleMissionGraph:
    """Minimal linear graph runner (can be swapped with LangGraph)."""

    def __init__(self) -> None:
        self.nodes: List[GraphNode] = []

    def add_node(self, name: str, handler: StepHandler) -> None:
        self.nodes.append(GraphNode(name=name, handler=handler))

    async def run(self, context: FlowContext) -> FlowContext:
        for node in self.nodes:
            context = await node(context)
        return context


def _log_agent_interaction(agent_name: str, action: str, detail: str | None = None) -> None:
    agent = AGENTS.get(agent_name)
    if agent:
        agent.log_to_pinkas(action, detail=detail)


def _get_agent(agent_name: str):
    if agent_name not in AGENTS:
        raise ValueError(f"Agent '{agent_name}' is not registered")
    return AGENTS[agent_name]


async def _call_agent(agent_name: str, context: FlowContext, payload: Any, stage: str) -> AgentResponse:
    agent = _get_agent(agent_name)
    _log_agent_interaction(agent_name, "start", detail=f"stage={stage}")
    response = await agent.run(
        AgentRequest(
            payload=payload,
            metadata={
                "user_id": context.user_id,
                "mission_type": context.mission_type,
                "stage": stage,
            },
        )
    )
    _log_agent_interaction(agent_name, "complete", detail=f"stage={stage}")
    context.history.append({"stage": stage, "agent": agent_name, "result": response.result})
    context.results[stage] = response
    return response


async def analyze_request(context: FlowContext) -> FlowContext:
    strategist_response = await _call_agent(
        "Strategist", context, context.payload, stage="analyze_request/strategist"
    )
    scholar_response = await _call_agent(
        "Scholar", context, context.payload, stage="analyze_request/scholar"
    )
    context.analysis = {
        "strategist": strategist_response.result,
        "scholar": scholar_response.result,
    }
    return context


async def plan_actions(context: FlowContext) -> FlowContext:
    ceo_response = await _call_agent("CEO", context, context.analysis or context.payload, stage="plan_actions/ceo")
    cto_response = await _call_agent("CTO", context, context.analysis or context.payload, stage="plan_actions/cto")
    context.plan = {
        "ceo": ceo_response.result,
        "cto": cto_response.result,
    }
    return context


async def execute_core_agent(context: FlowContext) -> FlowContext:
    core_payload = {
        "payload": context.payload,
        "analysis": context.analysis,
        "plan": context.plan,
    }
    execution_response = await _call_agent(
        context.primary_agent, context, core_payload, stage="execute_core_agent/primary"
    )
    context.execution = {"primary": execution_response.result}
    return context


async def finalize_message(context: FlowContext) -> FlowContext:
    evangelist_payload = {
        "user_id": context.user_id,
        "mission": context.mission_type,
        "execution": context.execution,
    }
    evangelist_response = await _call_agent(
        "Evangelist", context, evangelist_payload, stage="finalize_message/evangelist"
    )
    editor_payload = {
        "evangelist": evangelist_response.result,
        "history": context.history,
        "plan": context.plan,
    }
    editor_response = await _call_agent(
        "Editor", context, editor_payload, stage="finalize_message/editor"
    )
    context.final_message = str(editor_response.result)
    return context


def build_simple_graph() -> SimpleMissionGraph:
    graph = SimpleMissionGraph()
    graph.add_node("analyze_request", analyze_request)
    graph.add_node("plan_actions", plan_actions)
    graph.add_node("execute_core_agent", execute_core_agent)
    graph.add_node("finalize_message", finalize_message)
    return graph


async def run_simple_mission(context: FlowContext) -> FlowContext:
    graph = build_simple_graph()
    return await graph.run(context)


__all__ = [
    "FlowContext",
    "GraphNode",
    "SimpleMissionGraph",
    "run_simple_mission",
    "build_simple_graph",
]
