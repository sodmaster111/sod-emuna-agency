"""Treasury assessment utilities for the CFO agent."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Iterable, List


@dataclass
class InvestmentProposal:
    """Investment opportunity enriched with Kelly risk inputs."""

    name: str
    probability_of_success: Decimal
    return_multiple: Decimal
    notes: str | None = None
    max_fraction: Decimal | None = None

    def kelly_fraction(self) -> Decimal:
        """Return the Kelly Criterion fraction for this proposal.

        Kelly fraction = (b * p - q) / b, where b is the net odds (return_multiple
        minus 1), p is success probability, and q is failure probability. Negative
        fractions are floored at 0 to avoid recommending losses.
        """

        b = self.return_multiple - Decimal(1)
        p = self.probability_of_success
        q = Decimal(1) - p
        if b <= 0:
            return Decimal(0)
        fraction = (b * p - q) / b
        return max(Decimal(0), fraction)


def assess_treasury(
    current_balance: Decimal,
    obligations: Decimal,
    proposals: Iterable[InvestmentProposal],
    reserve_ratio: Decimal = Decimal("0.35"),
) -> dict[str, Any]:
    """Assess treasury health and provide Kelly-informed allocations.

    The CFO prioritizes reserves, covers short-term obligations, and then applies
    the Kelly Criterion on investment proposals to size risk-taking bets.
    """

    reserve_target = (current_balance * reserve_ratio).quantize(Decimal("0.000000001"))
    available_after_reserve = current_balance - obligations - reserve_target
    available_after_reserve = max(available_after_reserve, Decimal(0))

    proposal_assessments: List[dict[str, Any]] = []
    for proposal in proposals:
        kelly_pct = proposal.kelly_fraction()
        suggested_allocation = (available_after_reserve * kelly_pct).quantize(
            Decimal("0.000000001")
        )
        if proposal.max_fraction is not None:
            cap = available_after_reserve * proposal.max_fraction
            suggested_allocation = min(suggested_allocation, cap)

        expected_value = (
            proposal.return_multiple * proposal.probability_of_success
            - (Decimal(1) - proposal.probability_of_success)
        ) * suggested_allocation

        proposal_assessments.append(
            {
                "name": proposal.name,
                "kelly_fraction": kelly_pct,
                "suggested_allocation": suggested_allocation,
                "expected_value": expected_value.quantize(Decimal("0.000000001")),
                "notes": proposal.notes,
            }
        )

    liquidity_after_obligations = max(current_balance - obligations, Decimal(0))

    return {
        "current_balance": current_balance,
        "obligations": obligations,
        "reserve_target": reserve_target,
        "available_after_reserve": available_after_reserve,
        "liquidity_after_obligations": liquidity_after_obligations,
        "investment_plan": proposal_assessments,
    }


__all__ = ["InvestmentProposal", "assess_treasury"]
