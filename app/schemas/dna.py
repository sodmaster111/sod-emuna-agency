"""Pydantic schemas for validating the Corporate DNA registry."""
from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class DNAEntry(BaseModel):
    """Single agent DNA record."""

    model_config = ConfigDict(extra="forbid")

    display_name: str
    role: str
    tribe: str
    archetype: str
    dna_prompt: str
    responsibilities: List[str]
    tools: List[str]
    risk_profile: Optional[str] = None
    ethics_notes: Optional[str] = None


class DNARegistry(BaseModel):
    """Mapping of internal agent names to DNA entries."""

    model_config = ConfigDict(extra="forbid")

    __root__: Dict[str, DNAEntry]

    @property
    def entries(self) -> Dict[str, DNAEntry]:  # pragma: no cover - convenience property
        return self.__root__


__all__ = ["DNAEntry", "DNARegistry"]
