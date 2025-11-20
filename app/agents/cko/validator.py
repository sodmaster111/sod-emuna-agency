"""Halachic validation logic for proposed actions."""
from __future__ import annotations

from typing import Any, Dict, Tuple

import litellm

from app.agents.registry import AGENTS_CONFIG
from app.tools.torah import consult_sefaria

# High-risk keywords that warrant an immediate veto prior to LLM review.
AUTO_VETO_KEYWORDS = {
    "idolatry",
    "idol",
    "blasphemy",
    "heresy",
    "apostasy",
}


def _format_sources(sources: Dict[str, Any]) -> str:
    title = sources.get("title", "")
    text = sources.get("text", "")
    if isinstance(text, list):
        text = "\n".join(str(line) for line in text if line)
    return f"{title}\n{text}".strip()


def _interpret_llm_decision(raw_message: str) -> Tuple[str, str]:
    lowered = raw_message.lower()
    if any(keyword in lowered for keyword in ("reject", "veto", "forbid")):
        return "rejected", raw_message
    if "approve" in lowered or "permit" in lowered:
        return "approved", raw_message
    return "needs-review", raw_message


def validate_action(plan: str) -> Dict[str, Any]:
    """Validate an action plan against CKO halachic constraints.

    Steps:
    1. Query Sefaria for contextual sources.
    2. Ask an LLM (primed with the CKO system prompt) to veto if any conflict is
       detected.
    """

    sources = consult_sefaria(plan)
    system_prompt = AGENTS_CONFIG.get("CKO", {}).get("system_message", "")
    lower_plan = plan.lower()

    if any(keyword in lower_plan for keyword in AUTO_VETO_KEYWORDS):
        return {
            "plan": plan,
            "verdict": "rejected",
            "reason": "Automatic veto: conflicts with Torah fundamentals.",
            "sources": sources,
        }

    user_prompt = (
        "You are the CKO halachic validator. Review the proposed action for"
        " alignment with Torah, halacha, and ethical safeguards."
        f"\nPlan: {plan}"
        f"\nRelevant sources:\n{_format_sources(sources)}"
        "\nRespond with APPROVE or REJECT (or VETO) and a short rationale."
    )

    try:
        response = litellm.completion(
            model=getattr(litellm, "model", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        message = response["choices"][0]["message"]["content"]
        verdict, reason = _interpret_llm_decision(message)
    except Exception as exc:  # noqa: BLE001
        verdict, reason = "needs-review", f"LLM validation unavailable: {exc}"

    return {
        "plan": plan,
        "verdict": verdict,
        "reason": reason,
        "sources": sources,
    }


__all__ = ["validate_action"]
