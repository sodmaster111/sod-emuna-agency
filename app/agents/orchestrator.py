"""Mission orchestration layer for agent workflows.

Dependencies:
- langgraph (preferred for graph orchestration) – add to requirements.txt if available.
- If langgraph is unavailable in the environment, this module uses the internal simple
  flow runner defined in :mod:`app.agents.flows.simple_mission`.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict

from app.agents.flows.simple_mission import SimpleMissionFlow

logger = logging.getLogger(__name__)


class MissionType(str, Enum):
    """Enumeration of supported mission types."""

    PRAYER_DISTRIBUTION = "prayer_distribution"
    RESEARCH = "research"
    CONTENT_CREATION = "content_creation"


@dataclass
class MissionTask:
    """Incoming mission specification for the orchestrator."""

    mission_type: MissionType
    user_id: str | int
    payload: Dict[str, Any]


def select_primary_agent(mission_type: MissionType, payload: Dict[str, Any] | None = None) -> str:
    """Resolve the primary agent responsible for the mission.

    Args:
        mission_type: MissionType to route.
        payload: Optional payload for further disambiguation.

    Returns:
        The agent key registered in :mod:`app.agents.registry`.
    """

    payload = payload or {}

    if mission_type is MissionType.PRAYER_DISTRIBUTION:
        return "Evangelist"
    if mission_type is MissionType.RESEARCH:
        return "Researcher"
    if mission_type is MissionType.CONTENT_CREATION:
        # Choose based on desired output style.
        preferred_channel = payload.get("channel")
        if preferred_channel in {"visual", "design", "graphics"}:
            return "Designer"
        return "Editor"

    raise ValueError(f"Unsupported mission type: {mission_type}")


async def run_mission(task: MissionTask) -> Dict[str, Any]:
    """Entrypoint for executing a mission through the orchestration layer.

    Builds a graph-based flow for the mission, executes it, logs each step via
    individual agents' Pinkas logging, and returns a normalized result.
    """

    logger.info("Starting mission", extra={"mission_type": task.mission_type, "user_id": task.user_id})

    primary_agent = select_primary_agent(task.mission_type, task.payload)
    flow = SimpleMissionFlow(task=task, primary_agent=primary_agent)

    try:
        mission_result = await flow.run()
    except Exception as exc:  # pragma: no cover - orchestration-level safeguard
        logger.exception("Mission failed", exc_info=exc)
        return {
            "status": "failed",
            "summary": f"Mission failed: {exc}",
            "data": {"error": str(exc)},
        }

    summary = mission_result.get("summary", "Mission completed")
    return {"status": "success", "summary": summary, "data": mission_result}


async def execute_celery_mission(mission_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Adapter used by Celery tasks to execute a mission.

    Args:
        mission_payload: Raw payload received from Celery, expected to contain
            ``mission_type`` (str), ``user_id`` (str|int), and ``payload`` (dict).

    Returns:
        Normalized mission execution result.
    """

    mission_type = MissionType(mission_payload.get("mission_type"))
    user_id = mission_payload.get("user_id")
    payload = mission_payload.get("payload", {})

    task = MissionTask(mission_type=mission_type, user_id=user_id, payload=payload)
    return await run_mission(task)
