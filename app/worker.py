import asyncio
from datetime import datetime
from typing import Any, Dict

from celery import Celery

from app.agents.factory import AgentFactory
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.db.models import AgentLog, AgentTask

celery_app = Celery(
    "sod_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
celery_app.conf.task_routes = {"app.worker.execute_agent_task": {"queue": "agents"}}


async def _record_task_result(
    *,
    task_id: int,
    log_id: int,
    status: str,
    output: Dict[str, Any] | None = None,
    requires_cro_validation: bool,
):
    async with AsyncSessionLocal() as session:
        task = await session.get(AgentTask, task_id)
        if task:
            task.status = status
            if status == "completed":
                task.completed_at = datetime.utcnow()
            if requires_cro_validation and status == "completed":
                task.requires_cro_validation = "pending_cro_review"
            elif not requires_cro_validation:
                task.requires_cro_validation = "approved"

        log = await session.get(AgentLog, log_id)
        if log:
            log.status = status
            log.output_data = output or {}
        await session.commit()


async def _execute(agent_name: str, task_description: str, log_id: int, task_id: int, requires_cro_validation: bool):
    agent = AgentFactory.get_agent(agent_name)
    # Placeholder interaction with LLM/agent execution
    output = {
        "message": f"Executed task for {agent.name}",
        "task": task_description,
        "requires_cro_validation": requires_cro_validation,
    }

    if requires_cro_validation and agent_name != "CRO":
        output["status"] = "Awaiting CRO validation"
        status = "awaiting_cro_validation"
    else:
        status = "completed"

    await _record_task_result(
        task_id=task_id,
        log_id=log_id,
        status=status,
        output=output,
        requires_cro_validation=requires_cro_validation,
    )
    return output


@celery_app.task(name="app.worker.execute_agent_task")
def execute_agent_task(agent_name: str, task_description: str, log_id: int, task_id: int, requires_cro_validation: bool = True):
    return asyncio.run(
        _execute(
            agent_name=agent_name,
            task_description=task_description,
            log_id=log_id,
            task_id=task_id,
            requires_cro_validation=requires_cro_validation,
        )
    )
