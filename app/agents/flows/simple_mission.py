"""Simple mission flow using a sequential graph abstraction.

This module is designed to be compatible with LangGraph (preferred). If LangGraph
is not available, the ``SimpleMissionFlow`` uses an internal linear runner while
preserving the node-based structure so it can be swapped for LangGraph's graph
composition primitives.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Dict, List, MutableMapping

from app.agents import registry
from app.agents.base import BaseAgent
from app.agents.protocols import AgentRequest, AgentResponse

if TYPE_CHECKING:  # pragma: no cover - imported only for type checkers
    from app.agents.orchestrator import MissionTask

logger = logging.getLogger(__name__)


@dataclass
class FlowContext:
    """Context shared across nodes within the mission flow."""

    mission: MissionTask
    primary_agent: str
    state: MutableMapping[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)


class SimpleMissionFlow:
    """Minimal graph runner for orchestrating mission steps."""

    def __init__(self, task: MissionTask, primary_agent: str):
        self.task = task
        self.primary_agent = primary_agent
        self.context = FlowContext(mission=task, primary_agent=primary_agent)

        self.steps: List[Callable[[FlowContext], Any]] = [
            self.analyze_request,
            self.plan_actions,
            self.execute_core_agent,
            self.finalize_message,
        ]

    async def _run_agent(self, agent_name: str, payload: Any, step: str) -> AgentResponse:
        agent: BaseAgent = registry.AGENTS[agent_name]
        agent.log_to_pinkas("start", detail=f"mission={self.task.mission_type} step={step}")
        response = await agent.run(AgentRequest(payload=payload, metadata={"step": step}))
        agent.log_to_pinkas("complete", detail=f"mission={self.task.mission_type} step={step}")
        return response

    def _record_history(self, step: str, agent: str, response: AgentResponse) -> None:
        self.context.history.append(
            {
                "step": step,
                "agent": agent,
                "result": response.result,
                "metadata": response.metadata,
                "response_style": response.response_style,
            }
        )

    async def analyze_request(self, ctx: FlowContext) -> None:
        """Use Strategist and Scholar to refine the payload."""

        strategist_response = await self._run_agent(
            "Strategist",
            payload={"user_id": ctx.mission.user_id, "payload": ctx.mission.payload},
            step="analyze_request/strategist",
        )
        self._record_history("analyze_request", "Strategist", strategist_response)

        scholar_response = await self._run_agent(
            "Scholar",
            payload={"analysis": strategist_response.result, "payload": ctx.mission.payload},
            step="analyze_request/scholar",
        )
        self._record_history("analyze_request", "Scholar", scholar_response)

        ctx.state["analysis"] = {
            "strategist": strategist_response.result,
            "scholar": scholar_response.result,
        }

    async def plan_actions(self, ctx: FlowContext) -> None:
        """Plan route using CEO and CTO collaboration."""

        ceo_response = await self._run_agent(
            "CEO",
            payload={"analysis": ctx.state.get("analysis"), "payload": ctx.mission.payload},
            step="plan_actions/ceo",
        )
        self._record_history("plan_actions", "CEO", ceo_response)

        cto_response = await self._run_agent(
            "CTO",
            payload={"ceo_plan": ceo_response.result, "analysis": ctx.state.get("analysis")},
            step="plan_actions/cto",
        )
        self._record_history("plan_actions", "CTO", cto_response)

        ctx.state["plan"] = {"ceo": ceo_response.result, "cto": cto_response.result}

    async def execute_core_agent(self, ctx: FlowContext) -> None:
        """Run the primary agent determined by the orchestrator."""

        primary_response = await self._run_agent(
            ctx.primary_agent,
            payload={
                "plan": ctx.state.get("plan"),
                "analysis": ctx.state.get("analysis"),
                "mission_payload": ctx.mission.payload,
            },
            step="execute_core_agent",
        )
        self._record_history("execute_core_agent", ctx.primary_agent, primary_response)
        ctx.state["core_result"] = primary_response.result

    async def finalize_message(self, ctx: FlowContext) -> None:
        """Craft a friendly message using Evangelist and Editor."""

        evangelist_response = await self._run_agent(
            "Evangelist",
            payload={
                "core_result": ctx.state.get("core_result"),
                "plan": ctx.state.get("plan"),
                "user_id": ctx.mission.user_id,
            },
            step="finalize_message/evangelist",
        )
        self._record_history("finalize_message", "Evangelist", evangelist_response)

        editor_response = await self._run_agent(
            "Editor",
            payload={"evangelist_output": evangelist_response.result, "channel": ctx.mission.payload.get("channel")},
            step="finalize_message/editor",
        )
        self._record_history("finalize_message", "Editor", editor_response)

        ctx.state["final_message"] = editor_response.result

    async def run(self) -> Dict[str, Any]:
        """Execute the mission flow sequentially.

        The structure mirrors a LangGraph pipeline: each node receives the shared
        context, may mutate the state, and passes control to the next node.
        """

        for step in self.steps:
            logger.info("Running mission step", extra={"mission_type": self.task.mission_type, "step": step.__name__})
            await step(self.context)

        summary = str(self.context.state.get("final_message", "Mission completed"))
        return {
            "summary": summary,
            "history": self.context.history,
            "state": dict(self.context.state),
        }
