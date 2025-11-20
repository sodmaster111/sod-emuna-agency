"""Registry and seed logic for Digital Sanhedrin agents."""
from __future__ import annotations

from typing import Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent

AGENT_REGISTRY: Dict[str, Dict[str, object]] = {
    "CVO": {
        "name": "CVO",
        "role": "Chief Visionary Officer",
        "system_prompt": (
            "You are the Chief Visionary Officer. Focus on bold expansion, "
            "strategic partnerships, and transformative opportunities for the Digital Sanhedrin."
        ),
        "is_c_level": True,
    },
    "CKO": {
        "name": "CKO",
        "role": "Chief Knowledge Officer",
        "system_prompt": (
            "You are the Chief Knowledge Officer. Ensure every decision aligns with Torah and Halacha, "
            "providing rigorous validation for spiritual and legal correctness."
        ),
        "is_c_level": True,
    },
    "CFO": {
        "name": "CFO",
        "role": "Chief Financial Officer",
        "system_prompt": (
            "You are the Chief Financial Officer. Analyze risks and compliance impacts, especially "
            "around TON blockchain operations and treasury stewardship."
        ),
        "is_c_level": True,
    },
}


async def seed_agents(session: AsyncSession) -> None:
    """Populate the database with default agents if none exist."""

    existing = await session.execute(select(Agent))
    if existing.scalars().first():
        return

    for agent_data in AGENT_REGISTRY.values():
        session.add(Agent(**agent_data))
    await session.commit()


__all__ = ["AGENT_REGISTRY", "seed_agents"]
