"""Pydantic schemas for public API responses."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

try:  # Pydantic v2
    from pydantic import BaseModel, ConfigDict, Field

    class ORMBase(BaseModel):
        """Base model configured for ORM compatibility."""

        model_config = ConfigDict(from_attributes=True)

except ImportError:  # pragma: no cover - fallback for pydantic v1
    from pydantic import BaseModel, Field  # type: ignore

    class ORMBase(BaseModel):  # type: ignore[misc]
        class Config:
            orm_mode = True


class LogEntry(ORMBase):
    """Structured log details for council deliberations."""

    id: int
    timestamp: datetime
    agent: str
    message: str


class MissionRequest(ORMBase):
    """Payload describing the desired mission goal and current status."""

    goal: str = Field(..., description="Mission objective for the Sanhedrin council.")
    status: Optional[str] = Field(
        default=None, description="Operational state of the mission lifecycle."
    )


class StatusReport(ORMBase):
    """Health check and treasury summary details."""

    health: str = Field(..., description="Overall backend health indicator.")
    ton_balance: float = Field(
        ..., description="Current TON balance for the configured wallet."
    )
