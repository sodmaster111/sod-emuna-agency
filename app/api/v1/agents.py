"""Agent registry API endpoints."""
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.registry import seed_agents
from app.models.agent import Agent

router = APIRouter(prefix="/agents", tags=["agents"])


class ConsultationRequest(BaseModel):
    """Incoming payload to consult an agent."""

    query: str = Field(..., description="Question or task for the selected agent")


class AgentRead(BaseModel):
    """Serialized representation of an agent."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    role: str
    system_prompt: str
    is_c_level: bool


class ConsultationResponse(BaseModel):
    """Mock consultation response payload."""

    agent: AgentRead
    response: str


@router.post("/consult", response_model=ConsultationResponse)
async def consult_agent(
    payload: ConsultationRequest,
    session: AsyncSession = Depends(get_async_session),
) -> ConsultationResponse:
    """Select an agent from the registry and return a placeholder answer."""

    await seed_agents(session)

    result = await session.execute(select(Agent))
    agents = result.scalars().all()
    if not agents:
        raise HTTPException(status_code=503, detail="No agents available")

    selected_agent = next((agent for agent in agents if agent.is_c_level), agents[0])
    mock_response = (
        f"[Mocked] {selected_agent.role} '{selected_agent.name}' received: {payload.query}"
    )

    return ConsultationResponse(agent=selected_agent, response=mock_response)


@router.get("", response_model=List[AgentRead])
async def list_agents(session: AsyncSession = Depends(get_async_session)) -> List[AgentRead]:
    """Return all registered agents from the database."""

    await seed_agents(session)

    result = await session.execute(select(Agent))
    return list(result.scalars().all())


__all__ = ["router"]
