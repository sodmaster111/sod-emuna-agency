"""Simple stubbed board meeting simulation."""
from __future__ import annotations

from typing import Iterable

from .schemas import BoardDecision, Proposal, RoleOpinion


FORBIDDEN_KEYWORDS: set[str] = {"adult"}


def _contains_forbidden(content: Iterable[str]) -> bool:
    for value in content:
        lower_value = value.lower()
        for keyword in FORBIDDEN_KEYWORDS:
            if keyword in lower_value:
                return True
    return False


def simulate_board_meeting(proposal: Proposal) -> BoardDecision:
    """Simulate a board meeting for a given proposal using stubbed logic."""
    opinions: list[RoleOpinion] = []

    compliance_concern = _contains_forbidden([proposal.description, *proposal.tags])

    cpao_stance = "support"
    cpao_reasoning = "No compliance concerns detected."
    final_stance = "approved"

    if compliance_concern:
        cpao_stance = "against"
        cpao_reasoning = "Compliance flags forbidden content."
        final_stance = "rejected"

    cfo_stance = "support"
    cfo_reasoning = "Budget is clear and actionable."
    if proposal.budget_ton is None or proposal.budget_ton <= 0:
        cfo_stance = "neutral"
        cfo_reasoning = "Budget needs clarification or is missing."
        if final_stance != "rejected":
            final_stance = "needs_revision"

    opinions.append(
        RoleOpinion(
            role="ceo",
            stance="support" if final_stance == "approved" else "neutral",
            reasoning="Sees strategic value but defers to risk and budget signals.",
        )
    )

    opinions.append(
        RoleOpinion(
            role="cfo",
            stance=cfo_stance,
            reasoning=cfo_reasoning,
        )
    )

    opinions.append(
        RoleOpinion(
            role="cpao",
            stance=cpao_stance,
            reasoning=cpao_reasoning,
        )
    )

    opinions.append(
        RoleOpinion(
            role="cmo",
            stance="support" if not compliance_concern else "neutral",
            reasoning="Believes campaign can drive awareness." if not compliance_concern else "Marketing defers to compliance concerns.",
        )
    )

    summary_parts = [
        "CEO" + (" supports" if opinions[0].stance == "support" else " is cautious"),
        f"CFO {cfo_stance} due to budget assessment",
        f"CPAO {cpao_stance} on compliance review",
        "CMO supports marketing potential" if opinions[-1].stance == "support" else "CMO defers to compliance",
        f"Final stance: {final_stance}.",
    ]
    summary = "; ".join(summary_parts)

    return BoardDecision(
        proposal_id=proposal.id,
        summary=summary,
        final_stance=final_stance,
        opinions=opinions,
    )


if __name__ == "__main__":
    demo_proposal = Proposal(
        id="demo-001",
        title="Launch Tehillim Campaign",
        description="Launch new Tehillim campaign with outreach to global audience.",
        budget_ton=1000.0,
        tags=["community", "fundraising"],
    )
    decision = simulate_board_meeting(demo_proposal)
    print(decision.model_dump())
