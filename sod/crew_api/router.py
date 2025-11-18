from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from crewai import Crew, Task
from .agents import get_agent_registry


router = APIRouter(prefix="/missions", tags=["missions"])


class Mission(BaseModel):
    agent: str
    objective: str


@router.post("/run")
async def run_mission(m: Mission):
    registry = get_agent_registry()
    agent = registry.get(m.agent)

    if not agent:
        raise HTTPException(404, f"Agent '{m.agent}' not found")

    task = Task(
        description=m.objective,
        expected_output="טקסט קצר בעברית, מחזק, עדין ולא קיצוני.",
        agent=agent
    )

    crew = Crew(agents=[agent], tasks=[task])
    result = crew.kickoff()

    return {"agent": m.agent, "objective": m.objective, "result": str(result)}
