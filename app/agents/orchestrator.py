"""Mission orchestrator for the SOD-EMUNA agency.

Dependencies:
- Designed to integrate with `langgraph` or similar orchestration libraries.
  The backend already includes `langgraph` in `backend/requirements.txt`;
  ensure it is installed in the runtime environment.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict

from app.agents.flows.simple_mission import FlowContext, run_simple_mission
from app.agents.registry import AGENTS

logger = logging.getLogger(__name__)


class MissionType(str, Enum):
    PRAYER_DISTRIBUTION = "PRAYER_DISTRIBUTION"
    RESEARCH = "RESEARCH"
    CONTENT_CREATION = "CONTENT_CREATION"


@dataclass
class MissionTask:
    mission_type: MissionType
    user_id: str | int
    payload: Dict[str, Any]


def select_primary_agent(mission_type: MissionType, payload: Dict[str, Any] | None = None) -> str:
    """Route the mission to the most appropriate primary agent."""

    if mission_type is MissionType.PRAYER_DISTRIBUTION:
        return "Evangelist"
    if mission_type is MissionType.RESEARCH:
        return "Researcher"
    if mission_type is MissionType.CONTENT_CREATION:
        if payload and payload.get("requires_visuals"):
            return "Designer"
        return "Editor"
    raise ValueError(f"Unsupported mission type: {mission_type}")


async def run_mission(task: MissionTask) -> Dict[str, Any]:
    """Execute a mission by constructing and running the mission graph."""

    primary_agent = select_primary_agent(task.mission_type, task.payload)
    logger.info("Routing mission", extra={"mission_type": task.mission_type.value, "agent": primary_agent})

    context = FlowContext(
        mission_type=task.mission_type.value,
        user_id=task.user_id,
        payload=task.payload,
        primary_agent=primary_agent,
    )

    try:
        context = await run_simple_mission(context)
        summary = context.final_message or f"Mission {task.mission_type.value} completed by {primary_agent}"
        return {
            "status": "success",
            "summary": summary,
            "data": {
                "history": context.history,
                "analysis": context.analysis,
                "plan": context.plan,
                "execution": context.execution,
                "primary_agent": primary_agent,
            },
        }
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Mission execution failed", exc_info=exc)
        agent = AGENTS.get(primary_agent)
        if agent:
            agent.log_to_pinkas("error", detail=str(exc))
        return {"status": "failed", "summary": str(exc), "data": {}}


async def execute_celery_mission(mission_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Adapter for Celery tasks to execute missions asynchronously."""

    mission_type_value = mission_payload.get("mission_type")
    if not mission_type_value:
        raise ValueError("mission_type is required")

    mission_type = MissionType(mission_type_value)
    task = MissionTask(
        mission_type=mission_type,
        user_id=mission_payload.get("user_id", "anonymous"),
        payload=mission_payload.get("payload", {}),
    )
    return await run_mission(task)


__all__ = [
    "MissionTask",
    "MissionType",
    "select_primary_agent",
    "run_mission",
    "execute_celery_mission",
]
