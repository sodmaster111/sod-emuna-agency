"""Command scheduling endpoints for agents."""
from __future__ import annotations

from typing import Any, Dict, Optional

from celery import Celery
from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import registry as agent_registry
from app.api.deps import get_celery_app, get_db_session
from app.models.pinkas import Pinkas

router = APIRouter(prefix="/commands", tags=["commands"])


class ScheduleRequest(BaseModel):
    agent_name: str = Field(..., description="Registered agent identifier")
    payload: Dict[str, Any] = Field(default_factory=dict)


class ScheduleResponse(BaseModel):
    task_id: str
    agent_name: str


class CommandStatus(BaseModel):
    task_id: str
    state: str
    result: Optional[Dict[str, Any]] = None


@router.post("/schedule", response_model=ScheduleResponse)
async def schedule_command(
    request: ScheduleRequest,
    db: AsyncSession = Depends(get_db_session),
    celery_app: Celery = Depends(get_celery_app),
) -> ScheduleResponse:
    """Validate an agent and queue work on Celery while recording to Pinkas."""

    if request.agent_name not in agent_registry.AGENTS:
        raise HTTPException(status_code=400, detail="Unknown agent")

    log_entry = Pinkas(
        agent=request.agent_name,
        thought="command schedule",
        action="schedule",
        payload=request.payload,
        status="queued",
    )
    db.add(log_entry)
    await db.commit()
    await db.refresh(log_entry)

    task: AsyncResult = celery_app.send_task(
        "app.celery_worker.run_agent_task",
        kwargs={"agent_role": request.agent_name, "instruction": str(request.payload)},
    )

    return ScheduleResponse(task_id=task.id, agent_name=request.agent_name)


@router.get("/status/{task_id}", response_model=CommandStatus)
async def get_command_status(
    task_id: str,
    celery_app: Celery = Depends(get_celery_app),
) -> CommandStatus:
    """Inspect a Celery task state."""

    task: AsyncResult = celery_app.AsyncResult(task_id)
    result_payload: Optional[Dict[str, Any]] = None
    if task.successful() and isinstance(task.result, dict):
        result_payload = task.result  # type: ignore[assignment]

    return CommandStatus(task_id=task_id, state=task.state, result=result_payload)
