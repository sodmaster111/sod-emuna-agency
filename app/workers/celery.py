"""Celery worker configuration with audit logging to Pinkas."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from celery import Celery, Task, signals
from kombu import Queue

from app.core.config import settings
from app.db.session import async_session_factory
from app.models.pinkas import Pinkas

logger = logging.getLogger(__name__)

celery_app = Celery(
    "agents",
    broker=settings.redis_url,
    backend=settings.redis_url,
)
celery_app.conf.update(
    worker_concurrency=2,
    task_default_queue="agents",
    task_queues=(Queue("agents"),),
    task_acks_late=True,
    result_extended=True,
)


class AgentTask(Task):
    """Base Celery task with automatic retries."""

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 5}
    retry_backoff = True
    retry_jitter = True


celery_app.Task = AgentTask


def _get_agent_name(task: Task | None) -> str:
    return task.name if task and task.name else "unknown"


async def _write_pinkas_entry(
    *,
    agent: str,
    action: str,
    status: str,
    payload: Any | None = None,
    meta: dict[str, Any] | None = None,
) -> None:
    """Persist a Pinkas entry asynchronously."""

    async with async_session_factory() as session:
        record = Pinkas(agent=agent, action=action, status=status, payload=payload, meta=meta)
        session.add(record)
        await session.commit()


@signals.task_success.connect
def log_task_success(sender: Task | None = None, result: Any | None = None, **kwargs: Any) -> None:
    agent_name = _get_agent_name(sender)
    meta = {"task_id": kwargs.get("task_id")}
    asyncio.run(
        _write_pinkas_entry(agent=agent_name, action="task_complete", status="success", payload=result, meta=meta)
    )


@signals.task_failure.connect
def log_task_failure(sender: Task | None = None, exception: Exception | None = None, **kwargs: Any) -> None:
    agent_name = _get_agent_name(sender)
    meta = {"task_id": kwargs.get("task_id"), "traceback": kwargs.get("traceback")}
    payload = {"exception": str(exception) if exception else None}
    asyncio.run(
        _write_pinkas_entry(agent=agent_name, action="task_complete", status="failure", payload=payload, meta=meta)
    )


__all__ = ["celery_app", "AgentTask"]
