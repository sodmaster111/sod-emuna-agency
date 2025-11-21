"""TON treasury flow with CPAO enforcement for high-value transfers."""
from __future__ import annotations

import logging
from typing import Any, Dict

from app.services.cpao_client import CPAOInput, cpao_client
from app.services.ton_treasury import TonTreasury

logger = logging.getLogger(__name__)

THRESHOLD_REVIEW: float = 1000.0


async def request_ton_transfer(amount_ton: float, to_address: str, meta: Dict[str, Any] | None = None) -> dict:
    """Request a TON transfer gated by CPAO evaluation."""

    payload = {
        "amount_ton": amount_ton,
        "to_address": to_address,
        "meta": meta,
        "threshold_review": amount_ton >= THRESHOLD_REVIEW,
    }
    cpao_input = CPAOInput(
        actor="treasury_service",
        action_type="treasury.transfer",
        payload=payload,
    )

    judgement = await cpao_client.cpao_evaluate(cpao_input)
    logger.info(
        "CPAO decision for TON transfer: decision=%s risk_level=%s reasons=%s", 
        judgement.decision,
        judgement.risk_level,
        judgement.reasons,
    )

    if judgement.decision == "veto":
        return {
            "status": "blocked",
            "reason": "cpao_veto",
            "details": judgement.reasons,
        }

    if judgement.decision == "review_required":
        return {
            "status": "pending_review",
            "reason": "cpao_review_required",
            "details": judgement.reasons,
        }

    if amount_ton >= THRESHOLD_REVIEW and judgement.decision == "allow":
        return {
            "status": "pending_review",
            "reason": "threshold_review",
            "details": judgement.reasons,
        }

    treasury = await TonTreasury.from_env()
    tx_info = await treasury.send(
        to_address=to_address,
        amount=amount_ton,
        message=(meta or {}).get("memo"),
    )
    return {"status": "submitted", "tx": tx_info}
