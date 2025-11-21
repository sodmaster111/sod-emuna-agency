"""Schemas for defining AMAC roles and registries."""

from typing import Optional

from pydantic import BaseModel


class RoleDNA(BaseModel):
    """Represents the configuration for a single AMAC role."""

    internal_name: str
    display_name: str
    tribe: str
    mission: str
    dna_prompt: str
    responsibilities: list[str]
    tools: list[str]
    risk_profile: Optional[str] = None
    ethics_notes: Optional[str] = None


class RolesRegistry(BaseModel):
    """Collection of AMAC roles keyed by their internal names."""

    roles: dict[str, RoleDNA]


__all__ = ["RoleDNA", "RolesRegistry"]
