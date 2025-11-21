"""Base agent definitions for the SOD-EMUNA agency."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable

from app.agents.protocols import AgentRequest, AgentResponse
from app.services import ai_audit_logger

logger = logging.getLogger(__name__)


@dataclass
class BaseAgent(ABC):
    """Abstract representation of an agent within the system."""

    name: str
    role: str
    description: str
    tools: Iterable[str] = field(default_factory=list)
    dna: dict | None = None

    @abstractmethod
    async def run(self, agent_input: AgentRequest) -> AgentResponse:
        """Execute the agent given the provided input."""

    async def audit_reasoning_steps(
        self, steps: Iterable[str], meta: dict | None = None
    ) -> None:
        """Persist reasoning steps when audit mode is enabled."""

        for i, step in enumerate(steps):
            await ai_audit_logger.log_step(
                agent_name=self.name,
                step_index=i,
                content=step,
                meta=meta or self.dna or {},
            )

    def log_to_pinkas(
        self, action: str, detail: str | None = None, metadata: dict | None = None
    ) -> None:
        """Persist an action to the Pinkas (mission ledger).

        This implementation currently forwards entries to the application logger;
        production deployments can replace this with database persistence.
        """

        message = f"[Pinkas] agent={self.name} action={action}"
        if detail:
            message = f"{message} detail={detail}"
        logger.info(message, extra={"dna": metadata or self.dna or {}})
