"""Celery worker configuration for on-demand agent execution."""
from __future__ import annotations

from celery import Celery

from app.core.config import config

celery_app = Celery(
    "sod_celery",
    broker=config.redis_url,
    backend=config.redis_url,
)

celery_app.conf.task_routes = {"app.celery_worker.run_agent_task": {"queue": "agents"}}
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]


@celery_app.task(name="app.celery_worker.run_agent_task")
def run_agent_task(agent_role: str, instruction: str) -> dict:
    """Initialize an agent on demand and execute the provided instruction."""

    from app.agents.registry import AGENT_ROLES, create_agent
    from app.core.kernel import create_kernel

    kernel = create_kernel(config)
    agent_meta = AGENT_ROLES.get(agent_role)
    if agent_meta is None:
        return {"status": "error", "message": f"Unknown agent role: {agent_role}"}

    agent = create_agent(agent_meta)
    response = agent.initiate_chat(message=instruction, kernel=kernel)
    return {
        "status": "completed",
        "agent": agent_role,
        "instruction": instruction,
        "response": response,
    }


__all__ = ["celery_app", "run_agent_task"]
