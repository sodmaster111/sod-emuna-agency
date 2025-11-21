"""Data schemas for board meeting simulation."""
from __future__ import annotations

from pydantic import BaseModel, Field


class Proposal(BaseModel):
    id: str
    title: str
    description: str
    budget_ton: float | None = None
    tags: list[str] = Field(default_factory=list)


class RoleOpinion(BaseModel):
    role: str
    stance: str  # "support", "neutral", "against"
    reasoning: str


class BoardDecision(BaseModel):
    proposal_id: str
    summary: str
    final_stance: str  # "approved", "needs_revision", "rejected"
    opinions: list[RoleOpinion]
