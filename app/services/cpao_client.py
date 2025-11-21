"""Lightweight CPAO evaluation client stub.

This client exposes the :func:`cpao_evaluate` coroutine used by backend
services to request alignment judgements. The implementation is intentionally
minimal; replace with the production client from AMAC-INT-001 when available.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class CPAOInput:
    """Input payload describing the action to evaluate."""

    actor: str
    action_type: str
    payload: Dict[str, Any]


@dataclass
class CPAOJudgement:
    """CPAO decision returned by the evaluator."""

    decision: str
    risk_level: str | None = None
    reasons: List[str] | None = None


class CPAOClient:
    """Placeholder CPAO client awaiting real implementation."""

    async def cpao_evaluate(self, cpao_input: CPAOInput) -> CPAOJudgement:
        # TODO: Replace with actual CPAO service call.
        return CPAOJudgement(decision="allow", risk_level="low", reasons=[])


cpao_client = CPAOClient()
"""Singleton instance used throughout the application."""
