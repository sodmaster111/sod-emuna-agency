from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.guardrails import require_cro_validation
from app.agents.registry import AGENT_REGISTRY
from app.core.database import get_db
from app.db.models import AgentLog, Task

router = APIRouter()


class ExecuteRequest(BaseModel):
    agent_name: str
    task: str


@router.post("/agents/execute")
@require_cro_validation
async def execute_agent(
    request: ExecuteRequest,
    db: AsyncSession = Depends(get_db),
):
    if request.agent_name not in AGENT_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Agent {request.agent_name} not found")

    agent = AGENT_REGISTRY[request.agent_name]

    task = Task(
        agent_name=request.agent_name,
        task_type="user_request",
        description=request.task,
        status="queued",
    )
    db.add(task)

    log = AgentLog(
        agent_name=request.agent_name,
        agent_role=agent["role"],
        action="execute_task",
        input_data={"task": request.task},
        status="queued",
    )
    db.add(log)

    await db.commit()
    await db.refresh(task)

    return {
        "agent": agent["name"],
        "task_id": task.id,
        "status": "queued",
        "message": "Task sent to Celery worker for processing",
    }


@router.get("/agents")
async def list_agents():
    return {
        "total": len(AGENT_REGISTRY),
        "agents": [
            {
                "name": agent["name"],
                "role": agent["role"],
                "department": agent["department"],
                "tools": agent["tools"],
            }
            for agent in AGENT_REGISTRY.values()
        ],
    }
