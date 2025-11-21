from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.factory import AgentFactory
from app.core.database import get_db
from app.db.models import Agent, AgentLog, AgentTask
from app.worker import execute_agent_task

router = APIRouter()


class ExecuteRequest(BaseModel):
    agent_name: str
    task: str


@router.post("/agents/execute")
async def execute_agent(request: ExecuteRequest, db: AsyncSession = Depends(get_db)):
    try:
        agent_profile = AgentFactory.get_agent(request.agent_name)
    except KeyError:
        raise HTTPException(status_code=404, detail="Agent not found")

    requires_cro_validation = request.agent_name != "CRO"

    existing_agent_result = await db.execute(select(Agent).where(Agent.name == agent_profile.name))
    db_agent = existing_agent_result.scalar_one_or_none()
    if not db_agent:
        db_agent = Agent(
            name=agent_profile.name,
            role=agent_profile.role,
            dna_prompt=agent_profile.dna_prompt,
            tools=agent_profile.tools,
        )
        db.add(db_agent)
        await db.flush()

    log_entry = AgentLog(
        agent_id=db_agent.id,
        agent_name=agent_profile.name,
        action="execute",
        input_data={"task": request.task},
        status="queued",
    )
    db.add(log_entry)

    task_record = AgentTask(
        agent_id=db_agent.id,
        description=request.task,
        status="queued",
        requires_cro_validation="pending" if requires_cro_validation else "approved",
    )
    db.add(task_record)
    await db.commit()
    await db.refresh(log_entry)
    await db.refresh(task_record)

    execute_agent_task.delay(
        agent_name=request.agent_name,
        task_description=request.task,
        log_id=log_entry.id,
        task_id=task_record.id,
        requires_cro_validation=requires_cro_validation,
    )

    return {
        "agent": agent_profile.name,
        "task": request.task,
        "status": "queued",
        "requires_cro_validation": requires_cro_validation,
        "message": "Task sent to Celery worker",
    }
