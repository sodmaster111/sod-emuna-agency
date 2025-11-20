"""Models for describing Digital Sanhedrin agent profiles."""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict

from sqlmodel import Field, SQLModel


class AgentTier(str, Enum):
    """Enumeration of supported agent seniority tiers."""

    C_LEVEL = "C-Level"
    SPECIALIST = "Specialist"


class AgentProfile(SQLModel, table=False):
    """A lightweight agent profile used for orchestration and discovery."""

    name: str
    role: str
    tier: AgentTier
    system_prompt: str
    tools_config: Dict[str, Any] = Field(default_factory=dict)
