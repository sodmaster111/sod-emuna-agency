"""Agent discovery and orchestration endpoints."""
from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.orchestrator import SanhedrinOrchestrator
from app.core.registry import list_agents
from app.models import AgentProfile, AgentTier

router = APIRouter(prefix="/agents", tags=["agents"])

orchestrator = SanhedrinOrchestrator()


class DebateRequest(BaseModel):
    task: str
    agent_names: Optional[List[str]] = None
    tiers: Optional[List[AgentTier]] = None
    include_specialists: bool = False


class DebateResponse(BaseModel):
    task: str
    participants: List[str]
    transcripts: List[Dict[str, str]]
    summary: str


@router.get("", response_model=List[AgentProfile])
def get_agents(tier: Optional[AgentTier] = Query(default=None)) -> List[AgentProfile]:
    """List available agents optionally filtered by tier."""

    return list_agents(tier=tier)


@router.post("/debate", response_model=DebateResponse)
def start_debate(payload: DebateRequest) -> DebateResponse:
    """Kick off a Sanhedrin round-table debate on a topic."""

    try:
        result = orchestrator.debate(
            task=payload.task,
            agent_names=payload.agent_names,
            tiers=payload.tiers,
            include_specialists=payload.include_specialists,
        )
        return DebateResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
