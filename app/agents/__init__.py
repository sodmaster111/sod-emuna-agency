"""Agent package for the Digital Sanhedrin."""

from app.agents.council import SanhedrinCouncil
from app.agents.registry import AGENTS_CONFIG

__all__ = ["AGENTS_CONFIG", "SanhedrinCouncil"]
