"""Validator that checks action plans against halachic sources."""
from __future__ import annotations

from typing import Dict, List, Tuple

import litellm

from app.core.engine import Engine
from app.rag.vector_store import TorahChunk, search_halacha


SYSTEM_PROMPT = (
    "You are a posek reviewing an agent's action plan. Use the provided Torah "
    "sources to determine if the plan complies with Jewish Law. Respond with "
    "clear reasoning."
)


def _format_sources(sources: List[TorahChunk]) -> str:
    formatted: List[str] = []
    for chunk in sources:
        formatted.append(
            f"{chunk.reference} (chunk {chunk.chunk_index}): {chunk.content}"
        )
    return "\n\n".join(formatted)


def _call_judge(plan: str, sources: List[TorahChunk]) -> Tuple[str, str]:
    engine = Engine()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Plan:\n" + plan + "\n\n" + "Sources:\n" + _format_sources(sources)
            ),
        },
    ]
    response = litellm.completion(
        model=engine.model,
        messages=messages,
        temperature=0.1,
        max_tokens=300,
    )
    content = response["choices"][0]["message"]["content"]
    verdict = "approved" if "approve" in content.lower() else "rejected"
    return verdict, content


def check_compliance(action_plan: str) -> Dict[str, object]:
    """Evaluate an action plan for halachic compliance using RAG context."""

    sources = search_halacha(action_plan, limit=4)
    if not sources:
        return {
            "decision": "undetermined",
            "reason": "No halachic sources were available for evaluation.",
            "sources": [],
        }

    decision, analysis = _call_judge(action_plan, sources)
    return {
        "decision": decision,
        "reason": analysis,
        "sources": [s.reference for s in sources],
    }


__all__ = ["check_compliance"]
