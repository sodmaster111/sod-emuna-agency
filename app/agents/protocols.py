"""Protocol definitions shared across the agent framework."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class AgentRequest:
    """Input provided to an agent."""

    payload: Any
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Standardized agent output."""

    agent: str
    result: Any
    response_style: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
