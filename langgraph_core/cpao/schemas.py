from __future__ import annotations

from pydantic import BaseModel, Field


class CPAOInput(BaseModel):
    actor: str
    action_type: str
    payload: dict


class CPAOJudgement(BaseModel):
    allowed: bool
    decision: str
    reasons: list[str]
    risk_level: str
    recommendations: list[str] = Field(default_factory=list)
