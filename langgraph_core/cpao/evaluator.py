from __future__ import annotations

from typing import Any

from .schemas import CPAOInput, CPAOJudgement


class CPAOEvaluator:
    def __init__(self, constitution: dict | None = None):
        self.constitution = constitution or self._default_constitution()

    def _default_constitution(self) -> dict[str, Any]:
        return {
            "content": {
                "gossip_keywords": [
                    "он сказал",
                    "она сказала",
                    "она такая",
                    "он такой",
                    "слух",
                    "сплет",
                ],
                "insults": ["idiot", "stupid", "dumb", "fool"],
            },
            "treasury": {
                "review_threshold": 1000,
                "doubtful_categories": ["doubtful"],
            },
            "recommendations": {
                "review_required": [
                    "Escalate to human rabbinic review for lashon hara or financial ethics.",
                    "Ensure alignment with Torah values and verified tzedaka targets.",
                ],
                "veto": [
                    "Redirect funds or content toward Torah-aligned, chesed-focused initiatives.",
                    "Remove gossip/insulting language and avoid aiding questionable organizations.",
                ],
                "allow": [
                    "Proceed while documenting alignment checks and positive intent.",
                ],
            },
        }

    def evaluate(self, inp: CPAOInput) -> CPAOJudgement:
        reasons: list[str] = []
        recommendations: list[str] = []
        decision = "allow"
        allowed = True

        if inp.action_type == "content.publish":
            text = str(inp.payload.get("text", "")).lower()
            gossip_keywords = self.constitution.get("content", {}).get("gossip_keywords", [])
            insults = self.constitution.get("content", {}).get("insults", [])

            if any(keyword in text for keyword in gossip_keywords):
                reasons.append("Potential lashon hara or gossip detected in content.")
            if any(insult in text for insult in insults):
                reasons.append("Insulting language found in content.")

            if reasons:
                decision = "review_required"
                allowed = False
        elif inp.action_type == "treasury.transfer":
            treasury_rules = self.constitution.get("treasury", {})
            review_threshold = treasury_rules.get("review_threshold", 1000)
            doubtful_categories = treasury_rules.get("doubtful_categories", [])

            try:
                amount = float(inp.payload.get("amount", 0))
            except (TypeError, ValueError):
                amount = 0

            target_category = str(inp.payload.get("target_category", "")).lower()

            if target_category in doubtful_categories:
                decision = "veto"
                allowed = False
                reasons.append("Target category marked as doubtful and not aligned with values.")
            elif amount > review_threshold:
                decision = "review_required"
                allowed = False
                reasons.append("Transfer amount exceeds review threshold.")
        else:
            reasons.append("No specific CPAO constraints triggered; default allow.")

        if decision == "veto":
            risk_level = "high"
        elif decision == "review_required":
            risk_level = "medium"
        else:
            risk_level = "low"

        if decision == "veto":
            recommendations = self.constitution.get("recommendations", {}).get("veto", [])
        elif decision == "review_required":
            recommendations = self.constitution.get("recommendations", {}).get("review_required", [])
        else:
            recommendations = self.constitution.get("recommendations", {}).get("allow", [])

        return CPAOJudgement(
            allowed=allowed,
            decision=decision,
            reasons=reasons or ["No issues detected under CPAO rules."],
            risk_level=risk_level,
            recommendations=recommendations,
        )

    def is_allowed(self, inp: CPAOInput) -> bool:
        judgement = self.evaluate(inp)
        return judgement.allowed
