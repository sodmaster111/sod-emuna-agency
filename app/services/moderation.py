"""Lightweight moderation utilities for harmful and halachic speech checks."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from importlib import util
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Detoxify is optional; the module will operate in stub mode if unavailable.
# To install, run: `pip install detoxify torch`
if util.find_spec("detoxify") is not None:
    from detoxify import Detoxify
else:  # pragma: no cover - optional dependency
    Detoxify = None  # type: ignore


@dataclass
class ToxicityScore:
    """Normalized toxicity score container."""

    score: float


class HarmClassifier:
    """Toxicity classifier that wraps Detoxify when available."""

    def __init__(self, model_name: str = "original-small") -> None:
        self.model_name = model_name
        self._model: Optional[object] = None

    def _load_model(self) -> None:
        if self._model is None and Detoxify is not None:
            logger.info("Loading Detoxify model", extra={"model": self.model_name})
            self._model = Detoxify(self.model_name)

    async def score_toxicity(self, text: str) -> Dict[str, float]:
        """Return a toxicity score using Detoxify when installed."""

        if not text:
            return {"score": 0.0}

        if Detoxify is None:
            logger.warning("Detoxify not installed; returning stub score")
            return {"score": 0.0}

        self._load_model()

        if self._model is None:  # pragma: no cover - defensive check
            return {"score": 0.0}

        loop = asyncio.get_running_loop()

        def _predict() -> ToxicityScore:
            prediction = self._model.predict(text)
            toxicity = prediction.get("toxicity", 0.0)
            return ToxicityScore(score=float(toxicity))

        result = await loop.run_in_executor(None, _predict)
        return {"score": result.score}


class HalachaRulesClassifier:
    """Rule-based checks for lashon hara related speech patterns."""

    gossip_patterns: List[str] = [
        "он сказал",
        "ты видел что",
        "говорят что",
    ]
    slander_patterns: List[str] = [
        "он плохой",
        "она ужасная",
    ]

    def check_rules(self, text: str) -> Dict[str, List[str]]:
        """Check for simple keyword-based halachic speech violations."""

        normalized = text.lower()
        violations: List[str] = []

        for pattern in self.gossip_patterns:
            if pattern in normalized:
                violations.append("gossip")
                break

        for pattern in self.slander_patterns:
            if pattern in normalized:
                violations.append("slander")
                break

        return {"violations": violations}


class ModerationEngine:
    """Aggregate moderation checks for user text."""

    def __init__(
        self,
        harm_classifier: Optional[HarmClassifier] = None,
        rules_classifier: Optional[HalachaRulesClassifier] = None,
    ) -> None:
        self.harm_classifier = harm_classifier or HarmClassifier()
        self.rules_classifier = rules_classifier or HalachaRulesClassifier()

    async def assess(self, text: str) -> Dict[str, object]:
        """Assess text for toxicity and halachic rule violations."""

        toxicity_result = await self.harm_classifier.score_toxicity(text)
        toxicity_score = float(toxicity_result.get("score", 0.0))

        rule_result = self.rules_classifier.check_rules(text)
        violations = rule_result.get("violations", [])

        allowed = toxicity_score <= 0.65 and len(violations) == 0
        if allowed:
            summary = "Allowed: no significant toxicity or halachic violations detected."
        else:
            summary = "Blocked: policy thresholds exceeded."

        return {
            "allowed": allowed,
            "toxicity": toxicity_score,
            "violations": violations,
            "summary": summary,
        }


__all__ = [
    "HarmClassifier",
    "HalachaRulesClassifier",
    "ModerationEngine",
]


if __name__ == "__main__":
    async def _example() -> None:
        engine = ModerationEngine()
        sample = "Он сказал, что она ужасная"
        result = await engine.assess(sample)
        print(result)

    asyncio.run(_example())
