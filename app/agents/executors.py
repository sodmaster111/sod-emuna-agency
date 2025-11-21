"""Celery executor interfaces for agent scheduling."""
from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any, Dict

from app.agents.base import BaseAgent
from app.agents.protocols import AgentRequest, AgentResponse

logger = logging.getLogger(__name__)


async def _log_pinkas(action: str, detail: str | None = None) -> None:
    message = f"[Pinkas] action={action}"
    if detail:
        message = f"{message} detail={detail}"
    logger.info(message)


async def schedule(agent_name: str, payload: Any) -> str:
    """Schedule an agent execution via Celery.

    This stub issues a task identifier and logs the intent to the Pinkas ledger.
    """

    task_id = str(uuid.uuid4())
    await _log_pinkas("schedule", f"agent={agent_name} task_id={task_id}")
    # In a live system this would enqueue the task on Celery.
    await asyncio.sleep(0)
    return task_id


async def status(task_id: str) -> Dict[str, Any]:
    """Retrieve status for a scheduled task."""

    await _log_pinkas("status", f"task_id={task_id}")
    # Placeholder status response. Replace with Celery backend query.
    await asyncio.sleep(0)
    return {"task_id": task_id, "state": "PENDING"}


class EchoAgent(BaseAgent):
    """Minimal agent for executor-driven invocations."""

    response_style: str

    def __init__(self, name: str, role: str, description: str, tools: list[str], response_style: str):
        super().__init__(name=name, role=role, description=description, tools=tools)
        self.response_style = response_style

    async def run(self, agent_input: AgentRequest) -> AgentResponse:
        self.log_to_pinkas("run", detail=f"payload={agent_input.payload}")
        return AgentResponse(
            agent=self.name,
            result=f"[{self.response_style}] {agent_input.payload}",
            response_style=self.response_style,
            metadata={"role": self.role, "tools": list(self.tools)},
        )
