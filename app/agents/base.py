"""Base agent definitions for the SOD-EMUNA agency."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable

from app.agents.protocols import AgentRequest, AgentResponse

logger = logging.getLogger(__name__)


@dataclass
class BaseAgent(ABC):
    """Abstract representation of an agent within the system."""

    name: str
    role: str
    description: str
    tools: Iterable[str] = field(default_factory=list)

    @abstractmethod
    async def run(self, agent_input: AgentRequest) -> AgentResponse:
        """Execute the agent given the provided input."""

    def log_to_pinkas(self, action: str, detail: str | None = None) -> None:
        """Persist an action to the Pinkas (mission ledger).

        This implementation currently forwards entries to the application logger;
        production deployments can replace this with database persistence.
        """

        message = f"[Pinkas] agent={self.name} action={action}"
        if detail:
            message = f"{message} detail={detail}"
        logger.info(message)
