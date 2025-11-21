from __future__ import annotations

import inspect
from datetime import datetime
from typing import Any, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.amac_proposal import AMACProposal


async def generate_proposals_from_metrics(
    session: AsyncSession, limit: int = 10
) -> list[AMACProposal]:
    """Create proposal records based on recent mission metrics.

    This implementation stubs metric analysis by inserting canned proposals.
    """

    canned_candidates: list[dict[str, Any]] = [
        {
            "title": "Boost retention campaign",
            "description": (
                "Recent engagement dipped below target. Launch a retention-focused "
                "messaging sequence with personalized follow-ups."
            ),
            "budget_ton": 2500.0,
            "tags": ["engagement", "retention", "messaging"],
        },
        {
            "title": "Expand outreach to new segments",
            "description": (
                "Outbound response rates are strong; allocate budget to expand outreach "
                "into adjacent audience segments and A/B test creatives."
            ),
            "budget_ton": 1800.0,
            "tags": ["outreach", "growth", "experimentation"],
        },
    ][:limit]

    proposals: List[AMACProposal] = []
    for candidate in canned_candidates:
        proposal = AMACProposal(
            title=candidate["title"],
            description=candidate["description"],
            budget_ton=candidate.get("budget_ton"),
            tags=candidate.get("tags", []),
            status="pending",
        )
        session.add(proposal)
        proposals.append(proposal)

    await session.commit()
    for proposal in proposals:
        await session.refresh(proposal)

    return proposals


async def run_board_for_proposal(session: AsyncSession, proposal: AMACProposal) -> AMACProposal:
    """Run board simulation for a single proposal and persist the decision."""

    from app.services.board_sim_client import run_board_simulation

    board_request = {
        "title": proposal.title,
        "description": proposal.description,
        "budget_ton": proposal.budget_ton,
        "tags": proposal.tags or [],
        "metadata": {"proposal_id": str(proposal.id)},
    }

    decision = run_board_simulation(board_request)
    if inspect.isawaitable(decision):
        decision = await decision

    decision_payload: Any = decision
    if hasattr(decision, "model_dump"):
        decision_payload = decision.model_dump()
    elif hasattr(decision, "dict"):
        decision_payload = decision.dict()
    elif hasattr(decision, "__dict__"):
        decision_payload = {**decision.__dict__}

    proposal.board_decision = decision_payload

    final_stance = None
    if isinstance(decision_payload, dict):
        final_stance = decision_payload.get("final_stance")
    elif hasattr(decision, "final_stance"):
        final_stance = getattr(decision, "final_stance")

    status_map = {
        "approved": "approved",
        "rejected": "rejected",
        "needs_revision": "needs_revision",
    }
    proposal.status = status_map.get(str(final_stance).lower(), proposal.status)
    proposal.updated_at = datetime.utcnow()

    session.add(proposal)
    await session.commit()
    await session.refresh(proposal)

    return proposal


async def process_pending_proposals(session: AsyncSession, batch_size: int = 5) -> list[AMACProposal]:
    """Fetch pending proposals and process them through the board simulation."""

    result = await session.execute(
        select(AMACProposal).where(AMACProposal.status == "pending").limit(batch_size)
    )
    pending = list(result.scalars().all())

    processed: list[AMACProposal] = []
    for proposal in pending:
        updated = await run_board_for_proposal(session, proposal)
        processed.append(updated)

    return processed
